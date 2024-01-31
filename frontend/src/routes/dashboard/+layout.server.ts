import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load = (async ({ cookies }) => {
    if (cookies.get('sessionId') === undefined) redirect(301, '/')
}) satisfies LayoutServerLoad;