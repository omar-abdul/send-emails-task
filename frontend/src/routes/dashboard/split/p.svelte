<!-- <script lang="ts">
	import { invalidate } from '$app/navigation';
	import { onMount } from 'svelte';
	export let data;
	let interval: NodeJS.Timeout;
	let anchorEl: HTMLAnchorElement;
	onMount(() => {
		interval = setInterval(() => {
			invalidate(`/api/split_task?task=${data.task}&file=${data.file}`);
		}, 2000);

		if (data?.link) {
			anchorEl.click();
		}

		return () => {
			clearInterval(interval);
		};
	});

	$: done = data?.status.toLocaleLowerCase() === 'success';
	$: failed = data?.status.toLocaleLowerCase() === 'failure';
	$: done && clearInterval(interval);
	$: {
		if (data?.link) {
			if (anchorEl) anchorEl.click();
		}
	}
</script>

<main class="min-h-screen flex flex-col justify-center items-center">
	<div class="p-4">
		{#if data?.status.toLocaleLowerCase() === 'pending'}
			<span class="loading loading-ball loading-lg"></span>
			<p class={`text-sm  ${done ? 'text-green-500' : 'text-primary'} capitalize`}>
				{data?.status}
			</p>
		{:else if done}
			<p class="text-lg text-accent">
				DOWNLOAD SHOULD BEGIN SHORTLY IF IT DOESNT BEGIN <a
					href={data?.link}
					class="text-primary"
					download
					bind:this={anchorEl}>CLICK HERE</a
				>
			</p>
		{/if}
	</div>
</main> -->
