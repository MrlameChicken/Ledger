<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { page } from '$app/stores';
  import { apiRequest } from '$lib/api';
  import { authStore } from '$lib/stores/auth';

  interface Ledger {
    id: string;
    name: string;
  }

  interface User {
    id: string;
    email: string;
    full_name?: string | null;
  }

  interface ExpenseSplit {
    id: string;
    user_id: string;
    amount: string;
  }

  interface Expense {
    id: string;
    ledger_id: string | null;
    payer_id: string;
    title: string;
    amount: string;
    currency: string;
    category: string;
    notes?: string | null;
    occurred_at: string;
    splits: ExpenseSplit[];
  }

  let ledgers: Ledger[] = [];
  let selectedLedgerId: string | null = null;
  let members: User[] = [];
  let expenses: Expense[] = [];
  let currentUser: User | null = null;
  let error: string | null = null;
  let loading = true;

  let title = '';
  let amount = '';
  let category = 'general';
  let notes = '';
  let occurredAt = '';
  let selectedParticipantIds: string[] = [];

  function token() {
    return get(authStore).accessToken;
  }

  async function fetchCurrentUser() {
    const access = token();
    if (!access) throw new Error('Authentication required');
    currentUser = await apiRequest<User>('/users/me', { token: access });
  }

  async function fetchLedgers() {
    const access = token();
    if (!access) throw new Error('Authentication required');
    ledgers = await apiRequest<Ledger[]>('/ledgers/', { token: access });
    if (ledgers.length > 0 && !selectedLedgerId) {
      const currentPage = get(page);
      selectedLedgerId = currentPage.url.searchParams.get('ledger') ?? ledgers[0].id;
    }
  }

  async function fetchMembers() {
    if (!selectedLedgerId) return;
    const access = token();
    if (!access) throw new Error('Authentication required');
    members = await apiRequest<User[]>(`/ledgers/${selectedLedgerId}/members`, { token: access });
    if (currentUser && !members.find((member) => member.id === currentUser?.id)) {
      members = [currentUser, ...members];
    }
    if (members.length > 0) {
      selectedParticipantIds = members.map((member) => member.id);
    }
  }

  async function fetchExpenses() {
    const access = token();
    if (!access) throw new Error('Authentication required');
    const query = selectedLedgerId ? `?ledger_id=${selectedLedgerId}` : '';
    expenses = await apiRequest<Expense[]>(`/expenses/${query}`, { token: access });
  }

  async function loadData() {
    loading = true;
    error = null;
    try {
      await fetchCurrentUser();
      await fetchLedgers();
      await fetchMembers();
      await fetchExpenses();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load expenses';
    } finally {
      loading = false;
    }
  }

  async function handleLedgerChange() {
    try {
      await fetchMembers();
      await fetchExpenses();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to refresh ledger data';
    }
  }

  async function createExpense(event: Event) {
    event.preventDefault();
    if (!selectedLedgerId || !currentUser) {
      error = 'Ledger selection and authentication are required.';
      return;
    }
    if (selectedParticipantIds.length === 0) {
      error = 'Select at least one participant';
      return;
    }
    const access = token();
    if (!access) {
      error = 'Authentication required';
      return;
    }
    const total = parseFloat(amount);
    if (Number.isNaN(total)) {
      error = 'Enter a valid amount';
      return;
    }
    const centsTotal = Math.round(total * 100);
    const count = selectedParticipantIds.length;
    const baseShareCents = Math.floor(centsTotal / count);
    let distributed = 0;
    try {
      const expense = await apiRequest<Expense, Record<string, unknown>>('/expenses/', {
        method: 'POST',
        token: access,
        body: {
          ledger_id: selectedLedgerId,
          title,
          amount: total.toFixed(2),
          currency: 'USD',
          category,
          notes: notes || null,
          occurred_at: occurredAt ? new Date(occurredAt).toISOString() : undefined,
          splits: selectedParticipantIds.map((id, index) => {
            let shareCents = baseShareCents;
            distributed += shareCents;
            if (index === count - 1) {
              shareCents = centsTotal - (distributed - shareCents);
            }
            return { user_id: id, amount: (shareCents / 100).toFixed(2) };
          })
        }
      });
      expenses = [expense, ...expenses];
      title = '';
      amount = '';
      notes = '';
      occurredAt = '';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create expense';
    }
  }

  function toggleParticipant(id: string) {
    if (selectedParticipantIds.includes(id)) {
      selectedParticipantIds = selectedParticipantIds.filter((participant) => participant !== id);
    } else {
      selectedParticipantIds = [...selectedParticipantIds, id];
    }
  }

  onMount(loadData);
</script>

<section class="space-y-5">
  <h1 class="text-2xl font-semibold">Expenses</h1>
  {#if error}
    <p class="rounded bg-red-100 p-3 text-sm text-red-700">{error}</p>
  {/if}
  {#if ledgers.length === 0}
    <p class="rounded bg-yellow-100 p-3 text-sm text-yellow-800">Create a ledger before recording expenses.</p>
  {:else}
  <div class="grid gap-4 md:grid-cols-2">
    <form class="space-y-3 rounded border border-slate-200 bg-white p-4 shadow-sm" on:submit={createExpense}>
      <h2 class="text-lg font-medium">Add expense</h2>
      <label class="block">
        <span class="text-sm text-slate-600">Ledger</span>
        <select class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={selectedLedgerId} on:change={handleLedgerChange}>
          {#each ledgers as ledger}
            <option value={ledger.id}>{ledger.name}</option>
          {/each}
        </select>
      </label>
      <label class="block">
        <span class="text-sm text-slate-600">Title</span>
        <input class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={title} required />
      </label>
      <label class="block">
        <span class="text-sm text-slate-600">Amount (USD)</span>
        <input class="mt-1 w-full rounded border border-slate-300 p-2" type="number" min="0" step="0.01" bind:value={amount} required />
      </label>
      <label class="block">
        <span class="text-sm text-slate-600">Category</span>
        <input class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={category} />
      </label>
      <label class="block">
        <span class="text-sm text-slate-600">Date</span>
        <input class="mt-1 w-full rounded border border-slate-300 p-2" type="date" bind:value={occurredAt} />
      </label>
      <label class="block">
        <span class="text-sm text-slate-600">Notes</span>
        <textarea class="mt-1 w-full rounded border border-slate-300 p-2" rows="2" bind:value={notes} />
      </label>
      <div>
        <span class="text-sm text-slate-600">Participants</span>
        <div class="mt-2 space-y-2">
          {#each members as member}
            <label class="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                value={member.id}
                checked={selectedParticipantIds.includes(member.id)}
                on:change={() => toggleParticipant(member.id)}
              />
              <span>{member.full_name || member.email}</span>
            </label>
          {/each}
        </div>
      </div>
      <button class="rounded bg-blue-600 px-4 py-2 text-white" type="submit">Create expense</button>
    </form>

    <div class="space-y-3">
      {#if loading}
        <p>Loading expenses...</p>
      {:else if expenses.length === 0}
        <p>No expenses recorded yet.</p>
      {:else}
        {#each expenses as expense}
          <article class="space-y-2 rounded border border-slate-200 bg-white p-4 shadow-sm">
            <header class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">{expense.title}</h3>
              <span class="text-sm font-medium">${Number(expense.amount).toFixed(2)}</span>
            </header>
            <p class="text-sm text-slate-600">Category: {expense.category}</p>
            {#if expense.notes}
              <p class="text-sm text-slate-600">Notes: {expense.notes}</p>
            {/if}
            <p class="text-xs text-slate-500">{new Date(expense.occurred_at).toLocaleString()}</p>
            <div class="text-xs text-slate-500">
              Splits:
              <ul>
                {#each expense.splits as split}
                  <li>{split.user_id} - ${Number(split.amount).toFixed(2)}</li>
                {/each}
              </ul>
            </div>
          </article>
        {/each}
      {/if}
    </div>
  </div>
  {/if}
</section>
