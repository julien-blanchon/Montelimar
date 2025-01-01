/* eslint-disable @typescript-eslint/no-require-imports */
const defaultTheme = require('tailwindcss/defaultTheme')
const tailwindcssMotion = require('tailwindcss-motion')
const daisyui = require('daisyui')
const plugin = require('tailwindcss/plugin')
const { default: flattenColorPalette } = require("tailwindcss/lib/util/flattenColorPalette");

/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ["class"],
	content: ["./src/**/*.{html,js,svelte,ts}"],
	safelist: ["dark"],
	theme: {
		extend: {
			fontFamily: {
				sans: [...defaultTheme.fontFamily.sans]
			},
			keyframes: {
				"accordion-down": {
					from: { height: "0" },
					to: { height: "var(--bits-accordion-content-height)" },
				},
				"accordion-up": {
					from: { height: "var(--bits-accordion-content-height)" },
					to: { height: "0" },
				},
				"caret-blink": {
					"0%,70%,100%": { opacity: "1" },
					"20%,50%": { opacity: "0" },
				},
			},
			animation: {
				"accordion-down": "accordion-down 0.2s ease-out",
				"accordion-up": "accordion-up 0.2s ease-out",
				"caret-blink": "caret-blink 1.25s ease-out infinite",
			},
		},
	},
	plugins: [
		tailwindcssMotion,
		daisyui,
		/**
		 * @param {Object} param0
		 * @param {PluginAPI["matchUtilities"]} param0.matchUtilities
		 * @param {PluginAPI["addUtilities"]} param0.addUtilities
		 * @param {PluginAPI["theme"]} param0.theme
		 */
		plugin(function ({ matchUtilities, theme, addUtilities }) {		  
			matchUtilities(
				{
					'glow-radius': (value) => ({
						'--glow-radius': value,
					}),
				},
				{
					values: {
						'sm': '1px',
						'md': '5px',
						'lg': '10px',
						'xl': '15px',
						'2xl': '20px',
					},
					type: 'length',
				}
			);
			matchUtilities(
				{
					'glow-offset': (value) => ({
						'--glow-offset': value,
					}),
				},
				{
					values: {
						'sm': '1px',
						'md': '2px',
						'lg': '3px',
						'xl': '4px',
						'2xl': '5px',
					},
					type: 'length'
				}
			);
			matchUtilities(
				{
					'glow': (value) => ({
						'--glow-color': value,
						'filter': `drop-shadow(0px 0px var(--glow-radius, 10px) var(--glow-color))`,
					}),
				},
				{
					values: flattenColorPalette(theme('colors')),
					type: 'color',
				}
			);
			addUtilities({
				'.glow-none': {
					'--glow-color': 'transparent',
					'filter': 'none',
				},
			});
		}),
	],
	daisyui: {
		themes: false, // false: only light + dark | true: all themes | array: specific themes like this ["light", "dark", "cupcake"]
		darkTheme: "dark", // name of one of the included themes for dark mode
		base: false, // applies background color and foreground color for root element by default
		styled: true, // include daisyUI colors and design decisions for all components
		utils: true, // adds responsive and modifier utility classes
		prefix: "", // prefix for daisyUI classnames (components, modifiers and responsive class names. Not colors)
		logs: false, // Shows info about daisyUI version and used config in the console when building your CSS
		themeRoot: ":root", // The element that receives theme color CSS variables
	},
};
