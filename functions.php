<?php
/**
 * t.o.d. pink — Glitta. Block theme setup: styles, effects, patterns.
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
 * One pattern category so all t.o.d. sections sit together in the inserter.
 */
function tod_pink_pattern_category() {
	register_block_pattern_category(
		'tod-pink',
		array(
			'label'       => __( 't.o.d. pink', 'tod-pink' ),
			'description' => __( 'Sections of the TiTis on Decks night — hero, story, sets, dates, gallery, booking, finale.', 'tod-pink' ),
		)
	);
}
add_action( 'init', 'tod_pink_pattern_category' );
