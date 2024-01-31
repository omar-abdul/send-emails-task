<script lang="ts">
	import { goto } from '$app/navigation';
	import { redirect } from '@sveltejs/kit';
	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	export let data: PageData;

	onMount(() => {
		if (data.redirect) {
			goto('/dashboard/send-emails');
		}
	});
</script>
