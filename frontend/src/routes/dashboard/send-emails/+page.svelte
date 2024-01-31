<script lang="ts">
	import { enhance } from '$app/forms';
	import type { ActionData } from './$types';

	let loading = false;
	export let form: ActionData;
</script>

<main class="flex flex-col gap-3 justify-center items-center min-h-screen mt-4 p-3">
	{#if form?.success === false}<div class="bg-rose-400 text-rose-800 p-5 uppercase rounded-md">
			THERE WAS AN ERROR REFRESH THE PAGE AND SUBMIT AGAIN
		</div>{/if}
	<form
		class="flex flex-col gap-6 md:w-1/2 w-full shadow border dark:border-slate-50/15 border-slate-200 p-4"
		method="post"
		enctype="multipart/form-data"
		use:enhance={({}) => {
			loading = true;
			return async ({ update }) => {
				loading = false;
				update();
			};
		}}
	>
		<input
			type="file"
			name="file"
			class="file-input file-input-bordered w-full"
			placeholder="Select Shareholder pdf"
		/>
		<input type="text" name="subject" placeholder="Subject" class="input input-bordered w-full" />
		<textarea
			class="textarea textarea-primary"
			rows="8"
			name="message"
			placeholder="To include name of Shareholder write [magac] ex. Asc [magac]"
		></textarea>
		<button type="submit" class="btn btn-primary" disabled={loading}
			>{loading ? 'SUBMITTING' : 'SUBMIT'}
			{#if loading}<span class="loading loading-spinner text-primary"></span>{/if}</button
		>
	</form>
</main>
