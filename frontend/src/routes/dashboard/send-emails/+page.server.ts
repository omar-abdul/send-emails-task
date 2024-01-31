import { BACKEND_URL } from "$lib/constants";
import { redirect, type Actions } from "@sveltejs/kit";

export const actions = {
    default: async ({ request, cookies }) => {
        const data = await request.formData();
        data.append('refresh_token', cookies.get('refresh_token') || '');
        debugger;
        const response = await fetch(`${BACKEND_URL}/send-emails`, { method: "POST", body: data, headers: { 'Authorization': "Bearer " + cookies.get('sessionId') } });
        const res = await response.json();
        if (res.success) {

            redirect(301, '/dashboard/emails/?task=' + res.task_id);
        }
        return { success: res.success };
    }
} satisfies Actions;