import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (({ cookies }) => {

    redirect(301, '/dashboard/send-emails')
}) satisfies PageServerLoad;