<?php
/**
 * t.o.d. pink - Glitta. Block theme setup: styles, effects, patterns.
 *
 * @package tod-pink
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'TOD_PINK_VERSION', wp_get_theme()->get( 'Version' ) );

/**
 * Front-end assets: the embedded fonts, the ported night styles and the
 * vanilla effects file (spores, neon flicker, tilt, reveal, waveform).
 */
function tod_pink_enqueue_assets() {
	wp_enqueue_style(
		'tod-pink-fonts',
		get_theme_file_uri( 'assets/css/fonts.css' ),
		array(),
		TOD_PINK_VERSION
	);
	wp_enqueue_style(
		'tod-pink-style',
		get_theme_file_uri( 'assets/css/tod.css' ),
		array( 'tod-pink-fonts' ),
		TOD_PINK_VERSION
	);
	wp_enqueue_script(
		'tod-pink-effects',
		get_theme_file_uri( 'assets/js/tod.js' ),
		array(),
		TOD_PINK_VERSION,
		array( 'strategy' => 'defer', 'in_footer' => true )
	);
}
add_action( 'wp_enqueue_scripts', 'tod_pink_enqueue_assets' );

/**
 * The same look inside the editor, so Glitta edits in the real atmosphere.
 */
function tod_pink_editor_setup() {
	add_theme_support( 'editor-styles' );
	add_editor_style( array( 'assets/css/fonts.css', 'assets/css/tod.css' ) );
	add_theme_support( 'responsive-embeds' );
}
add_action( 'after_setup_theme', 'tod_pink_editor_setup' );

/**
 * EMOTIQ drop-in. The display stack is 'EMOTIQ', 'Audiowide', … - EMOTIQ
 * itself is never bundled (© Enxyclo Studio, license pending). The moment
 * a licensed file lands in assets/fonts/ (EMOTIQ.woff2, .woff, .otf or
 * .ttf, any capitalization), this registers its @font-face on the front
 * end and in the editor, and the stack picks it up. No file → Audiowide.
 */
function tod_pink_emotiq_face() {
	$formats = array(
		'woff2' => 'woff2',
		'woff'  => 'woff',
		'otf'   => 'opentype',
		'ttf'   => 'truetype',
	);
	$dir = get_theme_file_path( 'assets/fonts' );
	if ( ! is_dir( $dir ) ) {
		return '';
	}
	foreach ( scandir( $dir ) as $file ) {
		$ext = strtolower( pathinfo( $file, PATHINFO_EXTENSION ) );
		if ( 'emotiq' === strtolower( pathinfo( $file, PATHINFO_FILENAME ) ) && isset( $formats[ $ext ] ) ) {
			$url = get_theme_file_uri( 'assets/fonts/' . rawurlencode( $file ) );
			return "@font-face{font-family:'EMOTIQ';font-style:normal;font-weight:400;font-display:swap;src:url('{$url}') format('{$formats[ $ext ]}');}";
		}
	}
	return '';
}

function tod_pink_emotiq_enqueue() {
	$css = tod_pink_emotiq_face();
	if ( '' === $css ) {
		return;
	}
	wp_register_style( 'tod-pink-emotiq', false, array(), TOD_PINK_VERSION );
	wp_enqueue_style( 'tod-pink-emotiq' );
	wp_add_inline_style( 'tod-pink-emotiq', $css );
}
add_action( 'enqueue_block_assets', 'tod_pink_emotiq_enqueue' );

/**
 * One pattern category so all t.o.d. sections sit together in the inserter.
 */
function tod_pink_pattern_category() {
	register_block_pattern_category(
		'tod-pink',
		array(
			'label'       => __( 't.o.d. pink', 'tod-pink' ),
			'description' => __( 'Sections of the TiTis on Decks night - hero, story, sets, dates, gallery, booking, finale.', 'tod-pink' ),
		)
	);
}
add_action( 'init', 'tod_pink_pattern_category' );
