import { BACKEND_URL } from '$lib/constants';
import { error, json, type RequestHandler } from '@sveltejs/kit'

export const GET = (async ({ cookies, url }) => {

    const taskId = url.searchParams.get('task')
    const response = await fetch(`${BACKEND_URL}/email/task-status/${taskId}`, {
        headers: { Authorization: 'Bearer ' + cookies.get('sessionId') }
    });
    if (!response.ok) {
        console.log(response.status)
        error(500);
    }

    const { status, emails, result, zip_link }: { status: 'pending' | 'success' | 'failure', emails: { email: string; name: string; path: string }[], result?: string, zip_link: string } = await response.json();
    return json({ status, emails, result, zip_link })
}) satisfies RequestHandler