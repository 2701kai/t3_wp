<?php
/**
 * Title: Dates - Where the Dancing Is
 * Slug: tod-pink/dates
 * Categories: tod-pink
 * Description: Upcoming dates as rows: date in cyan, title, place. New date = duplicate a row.
 * Viewport Width: 1400
 */
?>
<!-- wp:group {"tagName":"section","anchor":"dates","className":"h-section","layout":{"type":"default"}} -->
<section class="wp-block-group h-section" id="dates">
	<!-- wp:group {"className":"h-head tod-reveal","layout":{"type":"default"}} -->
	<div class="wp-block-group h-head tod-reveal">
		<!-- wp:paragraph {"className":"h-kicker"} -->
		<p class="h-kicker">Dates</p>
		<!-- /wp:paragraph -->

		<!-- wp:heading {"className":"h-h2"} -->
		<h2 class="wp-block-heading h-h2">Where the <em>dancing</em> is</h2>
		<!-- /wp:heading -->
	</div>
	<!-- /wp:group -->

	<!-- wp:group {"className":"tod-dates tod-reveal","layout":{"type":"default"}} -->
	<div class="wp-block-group tod-dates tod-reveal">
		<!-- wp:group {"className":"tod-date","layout":{"type":"default"}} -->
		<div class="wp-block-group tod-date">
			<!-- wp:paragraph {"className":"tod-date-when"} -->
			<p class="tod-date-when">SAT · DD.MM.YYYY</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-what"} -->
			<p class="tod-date-what">Name of the night</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-where"} -->
			<p class="tod-date-where">Venue · Place</p>
			<!-- /wp:paragraph -->
		</div>
		<!-- /wp:group -->

		<!-- wp:group {"className":"tod-date","layout":{"type":"default"}} -->
		<div class="wp-block-group tod-date">
			<!-- wp:paragraph {"className":"tod-date-when"} -->
			<p class="tod-date-when">FRI · DD.MM.YYYY</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-what"} -->
			<p class="tod-date-what">Another night</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-where"} -->
			<p class="tod-date-where">Venue · Place</p>
			<!-- /wp:paragraph -->
		</div>
		<!-- /wp:group -->
	</div>
	<!-- /wp:group -->

	<!-- wp:paragraph {"className":"h-note"} -->
	<p class="h-note">New date: duplicate a row (⋮ → Duplicate), swap the texts. Past nights: delete them - or keep them as an archive.</p>
	<!-- /wp:paragraph -->
</section>
<!-- /wp:group -->
