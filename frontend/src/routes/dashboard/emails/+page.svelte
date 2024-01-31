<script lang="ts">
	import { onMount } from 'svelte';
	import { invalidate } from '$app/navigation';

	export let data;

	const { taskId } = data;

	let interval: NodeJS.Timeout;
	let anchorEl: HTMLAnchorElement;
	onMount(() => {
		if (taskId)
			interval = setInterval(() => {
				invalidate(`/api/email_task?task=${taskId}`);
			}, 5000);

		return () => {
			clearInterval(interval);
		};
	});

	$: done = data?.status.toLocaleLowerCase() === 'success';
	$: failed = data?.status.toLocaleLowerCase() === 'failure';
	$: (done || failed) && clearInterval(interval);
	$: {
		if (done) {
			anchorEl.href = data.zip_link;
			anchorEl.click();
		}
	}
</script>

<header class="flex justify-center items-center p-4">
	<a
		href="/dashboard/send-emails"
		class="underline hover:text-blue-800 text-blue-600 dark:text-blue-400">GO BACK TO FORM</a
	>
</header>
<main class="flex flex-col items-center min-h-screen w-full">
	{#if failed}
		<p class="text-3xl text-red-600">THERE WAS AN UNEXPECTED ERROR</p>
	{:else}
		<div class="flex justify-center items-center p-4">
			{#if !done}
				<span class="loading loading-ball loading-lg"></span>
			{/if}
			<p class={`text-sm  ${done ? 'text-green-500' : 'text-primary'} uppercase`}>
				{data?.status.toLocaleLowerCase() === 'pending' ? 'SENDING EMAILS...' : 'TASK COMPLETED'}
			</p>
			<!-- svelte-ignore a11y-missing-attribute -->
			<!-- svelte-ignore a11y-missing-content -->
		</div>
		<div class:hidden={!done} class="">
			<p class="text-sm uppercase">
				Any files that have not been sent will be available for download, if the download doesn't
				begin
			</p>
			<a bind:this={anchorEl} download class="text-sm underline hover:text-blue-600 text-blue-500"
				>CLICK HERE</a
			>
		</div>
		<div class="md:w-1/2 w-full rounded-md shadow-lg p-3 border dark:border-none">
			<div class="overflow-x-auto">
				<table class="table p-5">
					<!-- head -->
					<thead>
						<tr>
							<th></th>
							<th>Name</th>
							<th>Email</th>
							<th>PDF Link</th>
						</tr>
					</thead>

					<tbody>
						{#each data?.emails as email}
							<tr class="bg-base-200">
								<th></th>
								<td>{email.name}</td>
								<td>{email.email}</td>
								<td
									><a href={email.path} download class="underline text-primary, hover:text-blue-600"
										>PDF FILE</a
									></td
								>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</main>
