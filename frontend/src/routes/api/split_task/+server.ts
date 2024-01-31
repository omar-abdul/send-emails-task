import { BACKEND_URL } from '$lib/constants';
import { error, json, type RequestHandler } from '@sveltejs/kit'

export const GET = (async ({ cookies, url }) => {

    const taskId = url.searchParams.get('task');
    const filename = url.searchParams.get('file');
    const response = await fetch(`${BACKEND_URL}/split-and-zip/${taskId}/${filename}`, {
        headers: { Authorization: 'Bearer ' + cookies.get('sessionId') }
    });
    if (!response.ok) {
        console.log(response.statusText)
        error(500);
    }

    const { status, link }: { status: 'pending' | 'success' | 'failure', link: string } = await response.json();
    return json({ status, link })
}) satisfies RequestHandler