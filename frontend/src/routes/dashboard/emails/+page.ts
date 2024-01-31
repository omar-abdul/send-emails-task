import { BACKEND_URL } from "$lib/constants";
import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types"


export const load: PageLoad = async ({ url, fetch }) => {
    const taskId = url.searchParams.get('task');
    console.log('loaded')

    const response = await fetch(`/api/email_task?task=${taskId}`)
    if (!response.ok) {
        console.log(response.statusText)
    }
    const { status, emails, result, zip_link }: { status: 'pending' | 'success' | 'failure', emails: { email: string; name: string; path: string }[], result?: string, zip_link: string } = await response.json();
    console.log(result);
    return {
        taskId,
        status,
        emails,
        zip_link

    }

}