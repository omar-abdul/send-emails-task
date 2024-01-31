// import { error } from "@sveltejs/kit";
// import type { PageLoad } from "./$types";

// export const load = (async ({ fetch, url }) => {
//     const task = url.searchParams.get('task')
//     const file = url.searchParams.get('file')
//     const response = await fetch(`/api/split_task?task=${task}&file=${file}`);
//     if (!response.ok) {
//         error(500)
//     }
//     const { status, message, link }: { status: string, message: string | undefined, link: string | undefined } = await response.json();
//     return {
//         file,
//         task,
//         status,
//         message,
//         link
//     }
// }) satisfies PageLoad;