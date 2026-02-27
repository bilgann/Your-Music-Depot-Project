/*

I personnally believe we should use npm install next-auth

This would be great as it is open sourced and very easy to setup
for the real world field

You just import the SignIn function from next auth and Boom

Heres the link to check it out:
https://next-auth.js.org/

*/

export default function Login () {
    return (
        <div className='login-container'>
            <header>Login</header>

            <p>Email:</p>

            <input placeholder="Enter Email"></input>

            <p>Password:</p>

            <input placeholder="Enter Password"></input>

            <button>Show Password</button>

            <button>Sign In</button>
        </div>
    );
}