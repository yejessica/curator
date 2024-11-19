// components/Navbar.js
import Image from 'next/image';


const Navbar = ({ username }) => {
    const handleLogout = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/logout', {
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

    return (
        <div className="bg-gradient-to-r from-[#12171D] via-[rgba(7,68,89,0.2)] to-[rgba(0,0,0,0.2)] border-[#12171D] shadow-md flex items-start p-[20px_100px] justify-end space-x-[80px]">
            <div className="flex items-start space-x-[5px]">
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
