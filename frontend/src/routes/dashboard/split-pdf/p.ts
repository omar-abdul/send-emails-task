// import { BACKEND_URL } from "$lib/constants";
// import { redirect, type Actions, error } from "@sveltejs/kit";

// export const actions = {
//     default: async ({ request, cookies }) => {
//         const data = await request.formData();

//         const response = await fetch(`${BACKEND_URL}/split-pdf`, { method: "POST", body: data, headers: { 'Authorization': "Bearer " + cookies.get('sessionId') } });
//         if (!response.ok) {
//             error(500)
//         }
//         const res = await response.json();

//         if (res.status === 'pending') {
//             redirect(301, `/dashboard/split?task=${res.task}&file=${res.file}`)
//         }
//     }
// } satisfies Actions;