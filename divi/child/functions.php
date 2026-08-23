<?php
/**
 * t.o.d. pink - Glitta, as a Divi child theme.
 * Same night, same effects - Divi Builder does the editing.
 *
 * @package tod-pink-divi
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'TOD_PINK_DIVI_VERSION', wp_get_theme()->get( 'Version' ) );

/**
 * True while the Divi Visual Builder is editing the page. The effects
 * file must stay out then: split-text rewrites heading text nodes and
 * would fight the builder's inline editing.
 */
function tod_pink_divi_in_builder() {
	if ( isset( $_GET['et_fb'] ) ) {
		return true;
	}
	return function_exists( 'et_core_is_fb_enabled' ) && et_core_is_fb_enabled();
}

/**
 * Parent style, the night, the Divi glue and (outside the builder) the effects.
 */
function tod_pink_divi_enqueue() {
	wp_enqueue_style( 'divi-parent', get_template_directory_uri() . '/style.css', array(), TOD_PINK_DIVI_VERSION );
	wp_enqueue_style( 'tod-pink-fonts', get_stylesheet_directory_uri() . '/assets/css/fonts.css', array(), TOD_PINK_DIVI_VERSION );
	wp_enqueue_style( 'tod-pink-style', get_stylesheet_directory_uri() . '/assets/css/tod.css', array( 'tod-pink-fonts' ), TOD_PINK_DIVI_VERSION );
	wp_enqueue_style( 'tod-pink-divi-glue', get_stylesheet_directory_uri() . '/assets/css/divi-glue.css', array( 'tod-pink-style' ), TOD_PINK_DIVI_VERSION );
	wp_enqueue_style( 'tod-pink-g4-night', get_stylesheet_directory_uri() . '/assets/css/g4-night.css', array( 'tod-pink-divi-glue' ), TOD_PINK_DIVI_VERSION );

	if ( ! tod_pink_divi_in_builder() ) {
		/* g4-night.js goes FIRST, and the order is load-bearing. On a
		   cursor device the fluid is the atmosphere, so this script
		   removes the .tod-atmo host at parse time; tod.js then finds
		   nothing and never starts a second particle layer. Both are
		   deferred, so they run in document order. */
		wp_enqueue_script(
			'tod-pink-g4-night',
			get_stylesheet_directory_uri() . '/assets/js/g4-night.js',
			array(),
			TOD_PINK_DIVI_VERSION,
			array( 'strategy' => 'defer', 'in_footer' => true )
		);
		wp_enqueue_script(
			'tod-pink-effects',
			get_stylesheet_directory_uri() . '/assets/js/tod.js',
			array( 'tod-pink-g4-night' ),
			TOD_PINK_DIVI_VERSION,
			array( 'strategy' => 'defer', 'in_footer' => true )
		);
	}
}
add_action( 'wp_enqueue_scripts', 'tod_pink_divi_enqueue' );

/**
 * EMOTIQ drop-in, same contract as the block theme: place the licensed
 * file in assets/fonts/ as EMOTIQ.woff2/.woff/.otf/.ttf and the display
 * stack ('EMOTIQ', 'Audiowide', ...) picks it up. No file -> Audiowide.
 */
function tod_pink_divi_emotiq_face() {
	$formats = array(
		'woff2' => 'woff2',
		'woff'  => 'woff',
		'otf'   => 'opentype',
		'ttf'   => 'truetype',
	);
	$dir = get_stylesheet_directory() . '/assets/fonts';
	if ( ! is_dir( $dir ) ) {
		return '';
	}
	foreach ( scandir( $dir ) as $file ) {
		$ext = strtolower( pathinfo( $file, PATHINFO_EXTENSION ) );
		if ( 'emotiq' === strtolower( pathinfo( $file, PATHINFO_FILENAME ) ) && isset( $formats[ $ext ] ) ) {
			$url = get_stylesheet_directory_uri() . '/assets/fonts/' . rawurlencode( $file );
			return "@font-face{font-family:'EMOTIQ';font-style:normal;font-weight:400;font-display:swap;src:url('{$url}') format('{$formats[ $ext ]}');}";
		}
	}
	return '';
}

function tod_pink_divi_emotiq_enqueue() {
	$css = tod_pink_divi_emotiq_face();
	if ( '' === $css ) {
		return;
	}
	wp_register_style( 'tod-pink-emotiq', false, array(), TOD_PINK_DIVI_VERSION );
	wp_enqueue_style( 'tod-pink-emotiq' );
	wp_add_inline_style( 'tod-pink-emotiq', $css );
}
add_action( 'wp_enqueue_scripts', 'tod_pink_divi_emotiq_enqueue' );
