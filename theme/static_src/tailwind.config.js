/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // 🟢 Sahi path: Tumhara layout.html yahaan hai
    '../templates/**/*.html',

    // 🔄 Agar users, doctor, patients apps mein bhi Tailwind use kar rahe ho
    '../../users/templates/**/*.html',
    '../../doctor/templates/**/*.html',
    '../../patients/templates/**/*.html',

    // 🔄 Project-level templates (agar koi ho)
    '../../templates/**/*.html',

    // (Optional) JS files jisme Tailwind classes dynamically ho sakti hain
    // '../../**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
