// components/Navbar.js
'use client';
import Image from 'next/image';
import { useRouter } from 'next/navigation';



const Navbar = ({ username }) => {
    const router = useRouter();
    const handleLogout = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                console.log('Logged out successfully');
                window.location.href = '/login';
            } else {
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const goDashboard = () => {
        router.push('/dashboard');
    };


    

    return (
        <div className="bg-gradient-to-r from-[#12171D] via-[rgba(7,68,89,0.2)] to-[rgba(0,0,0,0.2)] border-[#12171D] shadow-md flex items-start p-[20px_100px] justify-end space-x-[80px]">
            <div className="flex items-start space-x-[5px]" role = "button" onClick = {goDashboard}>
                <Image
                    src="/profile-icon.svg"
                    width={28}
                    height={28}
                    alt="Profile Icon"
                />
                <p className="text-white font-helvetica text-[18px] font-bold">{username}</p>
            </div>

            <div
                role="button"
                className="flex items-start space-x-[5px]"
                onClick={handleLogout}
            >
                <Image
                    src="/logout-icon.svg"
                    width={28}
                    height={28}
                    alt="Logout Icon"
                />
                <p className="text-[#55D3FF] font-helvetica text-[18px] font-bold hover:text-[#9fe5ff]">
                    Logout
                </p>
            </div>
        </div>
    );
};

export default Navbar;
