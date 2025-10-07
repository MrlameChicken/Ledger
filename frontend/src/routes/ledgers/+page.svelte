<script lang="ts">
  import { onMount } from 'svelte';
  import { apiRequest } from '$lib/api';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';

  interface Ledger {
    id: string;
    name: string;
    description?: string | null;
    owner_id: string;
    created_at: string;
  }

  let ledgers: Ledger[] = [];
  let loading = true;
  let error: string | null = null;
  let name = '';
  let description = '';

  async function loadLedgers() {
    loading = true;
    error = null;
    try {
      const token = get(authStore).accessToken;
      if (!token) {
        throw new Error('Please sign in to view ledgers.');
      }
      ledgers = await apiRequest<Ledger[]>('/ledgers/', { token });
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load ledgers';
    } finally {
      loading = false;
    }
  }

  async function createLedger(event: Event) {
    event.preventDefault();
    error = null;
    try {
      const token = get(authStore).accessToken;
      if (!token) {
        throw new Error('Authentication required');
      }
      const ledger = await apiRequest<Ledger, Partial<Ledger>>('/ledgers/', {
        method: 'POST',
        token,
        body: { name, description }
      });
      ledgers = [ledger, ...ledgers];
      name = '';
      description = '';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create ledger';
    }
  }

  onMount(loadLedgers);
</script>

<section class="space-y-5">
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-semibold">Ledgers</h1>
  </div>
  <form class="space-y-3 rounded border border-slate-200 bg-white p-4 shadow-sm" on:submit={createLedger}>
    <h2 class="text-lg font-medium">Create new ledger</h2>
    <label class="block">
      <span class="text-sm text-slate-600">Name</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={name} required />
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Description</span>
      <textarea class="mt-1 w-full rounded border border-slate-300 p-2" rows="2" bind:value={description} />
    </label>
    <button class="rounded bg-blue-600 px-4 py-2 text-white" type="submit">Create ledger</button>
  </form>

  {#if loading}
    <p>Loading ledgers...</p>
  {:else if error}
    <p class="rounded bg-red-100 p-3 text-sm text-red-700">{error}</p>
  {:else if ledgers.length === 0}
    <p>No ledgers yet. Create one to get started.</p>
  {:else}
    <div class="grid gap-4 md:grid-cols-2">
      {#each ledgers as ledger}
        <article class="space-y-2 rounded border border-slate-200 bg-white p-4 shadow-sm">
          <h3 class="text-lg font-semibold">{ledger.name}</h3>
          {#if ledger.description}
            <p class="text-sm text-slate-600">{ledger.description}</p>
          {/if}
          <a class="text-sm text-blue-600 underline" href={`/expenses?ledger=${ledger.id}`}>
            View expenses
          </a>
        </article>
      {/each}
    </div>
  {/if}
</section>
