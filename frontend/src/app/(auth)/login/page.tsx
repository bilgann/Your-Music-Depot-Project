import React from 'react'

export default function LoginPage() {
    return (
        <div className='login-container'>
            <header>Login</header>

            <p>Email:</p>
            <input placeholder="Enter Email" />

            <p>Password:</p>
            <input placeholder="Enter Password" />

            <button>Show Password</button>
            <button>Sign In</button>
        </div>
    )
}
