// import Image from "next/image";
"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';


export default function Page() {
  const router = useRouter();

  useEffect(() => {
    router.push('/login');
  }, [router]);

  return null;
}
    