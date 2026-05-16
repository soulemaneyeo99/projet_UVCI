import { redirect } from 'next/navigation';

export default function RootPage() {
  // We don't want the root URL to hold any content, we just redirect it to the login page.
  redirect('/login');
}
