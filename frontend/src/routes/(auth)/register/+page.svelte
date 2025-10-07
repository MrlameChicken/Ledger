<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let email = '';
  let password = '';
  let fullName = '';
  let timezone = 'UTC';
  let error: string | null = null;
  let loading = false;

  async function handleSubmit(event: Event) {
    event.preventDefault();
    error = null;
    loading = true;
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName, timezone })
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Registration failed');
      }
      const loginForm = new URLSearchParams();
      loginForm.set('username', email);
      loginForm.set('password', password);
      const loginResponse = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: loginForm
      });
      if (!loginResponse.ok) {
        throw new Error('Automatic login failed, please log in manually');
      }
      const data = await loginResponse.json();
      authStore.setTokens(data.access_token, data.refresh_token);
      goto('/ledgers');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Registration failed';
    } finally {
      loading = false;
    }
  }
</script>

<section class="mx-auto max-w-md space-y-5">
  <h1 class="text-2xl font-semibold">Create account</h1>
  {#if error}
    <p class="rounded bg-red-100 p-3 text-sm text-red-700">{error}</p>
  {/if}
  <form class="space-y-4" on:submit={handleSubmit}>
    <label class="block">
      <span class="text-sm text-slate-600">Full name</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={fullName} />
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Email</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" type="email" bind:value={email} required />
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Password</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" type="password" bind:value={password} required minlength="8" />
    </label>
    <label class="block">
      <span class="text-sm text-slate-600">Timezone</span>
      <input class="mt-1 w-full rounded border border-slate-300 p-2" bind:value={timezone} />
    </label>
    <button class="w-full rounded bg-blue-600 px-4 py-2 text-white" type="submit" disabled={loading}>
      {#if loading}Creating account...{:else}Sign up{/if}
    </button>
  </form>
</section>
