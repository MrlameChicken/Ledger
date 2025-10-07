<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { derived } from 'svelte/store';

  const isAuthenticated = derived(authStore, ($auth) => Boolean($auth.accessToken));
</script>

{#if $isAuthenticated}
  <section class="space-y-4">
    <h1 class="text-2xl font-semibold">Welcome back!</h1>
    <p>Visit your <a class="text-blue-600 underline" href="/ledgers">ledgers</a> to manage shared expenses or review recent <a class="text-blue-600 underline" href="/expenses">expenses</a>.</p>
  </section>
{:else}
  <section class="mx-auto max-w-2xl space-y-5 text-center">
    <h1 class="text-3xl font-bold">Track and share expenses with ease</h1>
    <p class="text-slate-600">Ledger helps you keep a pulse on your personal spending and settle shared costs with friends, family, or teams.</p>
    <div class="flex justify-center gap-3">
      <a href="/register" class="rounded bg-blue-600 px-4 py-2 text-white">Get started</a>
      <a href="/login" class="rounded border border-blue-600 px-4 py-2 text-blue-600">I already have an account</a>
    </div>
  </section>
{/if}
