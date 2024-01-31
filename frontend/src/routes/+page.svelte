<script lang="ts">
	import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
	import { Mail } from 'lucide-svelte';
	import { PUBLIC_CLIENT_ID, PUBLIC_REDIRECT_URL } from '$env/static/public';
	function signInWithFirebase() {
		const provider = new GoogleAuthProvider();
		const auth = getAuth();
		signInWithPopup(auth, provider)
			.then((result) => {
				// This gives you a Google Access Token. You can use it to access the Google API.
				const credential = GoogleAuthProvider.credentialFromResult(result);
				const token = credential?.accessToken;
				// The signed-in user info.
				const user = result.user;
				// IdP data available using getAdditionalUserInfo(result)

				// ...
			})
			.catch((error) => {
				// Handle Errors here.
				const errorCode = error.code;
				const errorMessage = error.message;
				// The email of the user's account used.
				const email = error.customData.email;
				// The AuthCredential type that was used.
				const credential = GoogleAuthProvider.credentialFromError(error);
				// ...
			});
	}

	const googleAuthUrl = 'https://accounts.google.com/o/oauth2/v2/auth';
	// const redirectUri = 'https://shareapp.pages.dev/auth/callback'; // Replace with your redirect URI
	const redirectUri = PUBLIC_REDIRECT_URL; // Replace with your redirect URI

	const clientId = PUBLIC_CLIENT_ID;
	const scopes = [
		'https://www.googleapis.com/auth/gmail.send',
		'https://www.googleapis.com/auth/userinfo.email'
	];

	function createAuthUrl() {
		const params = new URLSearchParams({
			client_id: clientId,
			redirect_uri: redirectUri,
			response_type: 'code',
			scope: scopes.join(' '),
			access_type: 'offline', // For getting a refresh token
			prompt: 'consent'
		});
		return `${googleAuthUrl}?${params.toString()}`;
	}
</script>

<main class="flex flex-col justify-center items-center min-h-screen">
	<a href={createAuthUrl()} class="bg-gray-200 text-black p-5 rounded-md">
		<span><Mail class="text-red-600 inline" /> SIGN IN WITH GMAIL</span></a
	>
</main>
