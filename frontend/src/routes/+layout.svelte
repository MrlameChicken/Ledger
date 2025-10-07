<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { page } from '$app/stores';
  import { derived } from 'svelte/store';

  const isAuthenticated = derived(authStore, ($auth) => Boolean($auth.accessToken));

  function logout() {
    authStore.clear();
  }
</script>

<svelte:head>
  <title>Ledger</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 text-slate-900">
  <header class="border-b border-slate-200 bg-white">
    <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
      <a class="text-lg font-semibold" href="/">Ledger</a>
      {#if $isAuthenticated}
        <nav class="flex items-center gap-4 text-sm">
          <a href="/ledgers" class={$page.url.pathname.startsWith('/ledgers') ? 'font-semibold text-blue-600' : ''}>Ledgers</a>
          <a href="/expenses" class={$page.url.pathname.startsWith('/expenses') ? 'font-semibold text-blue-600' : ''}>Expenses</a>
          <a href="/settlements" class={$page.url.pathname.startsWith('/settlements') ? 'font-semibold text-blue-600' : ''}>Settlements</a>
          <button class="rounded bg-slate-100 px-3 py-1" on:click={logout}>Logout</button>
        </nav>
      {:else}
        <nav class="flex items-center gap-2 text-sm">
          <a href="/login" class="rounded bg-blue-600 px-3 py-1 text-white">Login</a>
          <a href="/register" class="rounded border border-blue-600 px-3 py-1 text-blue-600">Register</a>
        </nav>
      {/if}
    </div>
  </header>
  <main class="mx-auto max-w-5xl px-4 py-6">
    <slot />
  </main>
</div>

<style>
  @import url('https://cdn.jsdelivr.net/npm/tailwindcss@3.3.3/dist/tailwind.min.css');
  :global(body) {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: #f8fafc;
  }
  a {
    text-decoration: none;
    color: inherit;
  }
  button {
    cursor: pointer;
  }
</style>
