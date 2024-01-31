import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { BACKEND_URL } from "$lib/constants";

export const load = (async ({ url, fetch, cookies }) => {
    const sessionId = cookies.get('sessionId');
    const code = url.searchParams.get('code');

    if (sessionId) throw redirect(301, '/dashboard');

    // Process only if there is a code
    if (code) {
        const payload = { code };
        const response = await fetch(BACKEND_URL + '/exchange-token', {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
        });

        const token = await response.json();

        cookies.set('sessionId', token.access_token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60,
        });
        cookies.set('refresh_token', token.refresh_token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60,
        });

        return { redirect: true }
    }

    // If there's no code, handle accordingly
    // For example, redirect to a login page or show an error
    return { redirect: false }
}) satisfies PageServerLoad;
