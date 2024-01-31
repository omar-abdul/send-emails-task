import type { PageServerLoad } from './$types';
import { redirect } from "@sveltejs/kit";

export const load = (async ({cookies}) => {
    if(cookies.get("sessionId")!==undefined){
        redirect(301,'/dashboard');
    }
}) satisfies PageServerLoad;