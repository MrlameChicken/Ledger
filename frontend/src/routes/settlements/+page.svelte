<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { apiRequest } from '$lib/api';
  import { authStore } from '$lib/stores/auth';

  interface Ledger {
    id: string;
    name: string;
  }

  interface Settlement {
    id: string;
    ledger_id: string;
    from_user_id: string;
    to_user_id: string;
    amount: string;
    status: string;
    created_at: string;
    settled_at?: string | null;
  }

  interface User {
    id: string;
    email: string;
    full_name?: string | null;
  }

  let ledgers: Ledger[] = [];
  let settlements: Settlement[] = [];
  let members: User[] = [];
  let selectedLedgerId: string | null = null;
  let toUserId = '';
  let amount = '';
  let loading = true;
  let error: string | null = null;

  function token() {
    return get(authStore).accessToken;
  }

  async function fetchLedgers() {
    const access = token();
    if (!access) throw new Error('Authentication required');
    ledgers = await apiRequest<Ledger[]>('/ledgers/', { token: access });
    if (ledgers.length > 0 && !selectedLedgerId) {
      selectedLedgerId = ledgers[0].id;
    }
  }

  async function fetchMembers() {
    if (!selectedLedgerId) return;
    const access = token();
    if (!access) throw new Error('Authentication required');
    members = await apiRequest<User[]>(`/ledgers/${selectedLedgerId}/members`, { token: access });
  }

  async function fetchSettlements() {
    if (!selectedLedgerId) return;
    const access = token();
    settlements = await apiRequest<Settlement[]>(`/settlements/?ledger_id=${selectedLedgerId}`, { token: access });
  }

  async function loadData() {
    loading = true;
    error = null;
    try {
      await fetchLedgers();
      await fetchMembers();
      await fetchSettlements();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load settlements';
    } finally {
      loading = false;
    }
  }

  async function handleLedgerChange() {
    try {
      await fetchMembers();
      await fetchSettlements();
      toUserId = '';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to refresh ledger data';
    }
  }

  async function createSettlement(event: Event) {
    event.preventDefault();
    if (!selectedLedgerId || !toUserId) {
      error = 'Select a ledger and recipient';
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
    try {
      const settlement = await apiRequest<Settlement, Record<string, unknown>>('/settlements/', {
        method: 'POST',
        token: access,
        body: {
          ledger_id: selectedLedgerId,
          to_user_id: toUserId,
          amount: total.toFixed(2)
        }
      });
      settlements = [settlement, ...settlements];
      amount = '';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create settlement';
    }
  }

  async function confirmSettlement(id: string) {
    const access = token();
    if (!access) return;
    try {
      const settlement = await apiRequest<Settlement>(`/settlements/${id}/confirm`, {
        method: 'POST',
        token: access
      });
      settlements = settlements.map((item) => (item.id === id ? settlement : item));
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to confirm settlement';
    }
  }

  onMount(loadData);
</script>

<section class="space-y-5">
  <h1 class="text-2xl font-semibold">Settlements</h1>
  {#if error}
    <p class="rounded bg-red-100 p-3 text-sm text-red-700">{error}</p>
  {/if}
  {#if ledgers.length === 0}
    <p class="rounded bg-yellow-100 p-3 text-sm text-yellow-800">Create a ledger to start recording settlements.</p>
  {:else}
  <form class="space-y-3 rounded border border-slate-200 bg-white p-4 shadow-sm" on:submit={createSettlement}>
    <h2 class="text-lg font-medium">Record settlement</h2>
    <label class="block">
      <span class="text-sm text-slate-600">Ledger</span>
      <select class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={selectedLedgerId} on:change={handleLedgerChange}>
        {#each ledgers as ledger}
          <option value={ledger.id}>{ledger.name}</option>
        {/each}
      </select>
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Recipient</span>
      <select class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={toUserId}>
        <option value="" disabled>Choose member</option>
        {#each members as member}
          <option value={member.id}>{member.full_name || member.email}</option>
        {/each}
      </select>
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Amount</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" type="number" min="0" step="0.01" bind:value={amount} required />
    </label>
    <button class="rounded bg-blue-600 px-4 py-2 text-white" type="submit">Record settlement</button>
  </form>

  <div class="space-y-3">
    {#if loading}
      <p>Loading settlements...</p>
    {:else if settlements.length === 0}
      <p>No settlements recorded.</p>
    {:else}
      {#each settlements as settlement}
        <article class="space-y-2 rounded border border-slate-200 bg-white p-4 shadow-sm">
          <header class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">${Number(settlement.amount).toFixed(2)}</h3>
            <span class="text-sm font-medium">{settlement.status}</span>
          </header>
          <p class="text-sm text-slate-600">From: {settlement.from_user_id}</p>
          <p class="text-sm text-slate-600">To: {settlement.to_user_id}</p>
          <p class="text-xs text-slate-500">{new Date(settlement.created_at).toLocaleString()}</p>
          {#if settlement.status === 'pending'}
            <button class="rounded bg-green-600 px-3 py-1 text-white" on:click={() => confirmSettlement(settlement.id)}>
              Confirm receipt
            </button>
          {:else if settlement.settled_at}
            <p class="text-xs text-slate-500">Confirmed at {new Date(settlement.settled_at).toLocaleString()}</p>
          {/if}
        </article>
      {/each}
    {/if}
  </div>
  {/if}
</section>
