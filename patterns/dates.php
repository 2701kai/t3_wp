<?php
/**
 * Title: Termine — Wo getanzt wird
 * Slug: tod-pink/dates
 * Categories: tod-pink
 * Description: Die nächsten Dates als Zeilen: Datum in Cyan, Titel, Ort. Neue Zeile = Gruppe duplizieren.
 * Viewport Width: 1400
 */
?>
<!-- wp:group {"tagName":"section","anchor":"termine","className":"h-section","layout":{"type":"default"}} -->
<section class="wp-block-group h-section" id="termine">
	<!-- wp:group {"className":"h-head tod-reveal","layout":{"type":"default"}} -->
	<div class="wp-block-group h-head tod-reveal">
		<!-- wp:paragraph {"className":"h-kicker"} -->
		<p class="h-kicker">Termine</p>
		<!-- /wp:paragraph -->

		<!-- wp:heading {"className":"h-h2"} -->
		<h2 class="wp-block-heading h-h2">Wo <em>getanzt</em> wird</h2>
		<!-- /wp:heading -->
	</div>
	<!-- /wp:group -->

	<!-- wp:group {"className":"tod-dates tod-reveal","layout":{"type":"default"}} -->
	<div class="wp-block-group tod-dates tod-reveal">
		<!-- wp:group {"className":"tod-date","layout":{"type":"default"}} -->
		<div class="wp-block-group tod-date">
			<!-- wp:paragraph {"className":"tod-date-when"} -->
			<p class="tod-date-when">SA · TT.MM.JJJJ</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-what"} -->
			<p class="tod-date-what">Name der Nacht</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-where"} -->
			<p class="tod-date-where">Venue · Ort</p>
			<!-- /wp:paragraph -->
		</div>
		<!-- /wp:group -->

		<!-- wp:group {"className":"tod-date","layout":{"type":"default"}} -->
		<div class="wp-block-group tod-date">
			<!-- wp:paragraph {"className":"tod-date-when"} -->
			<p class="tod-date-when">FR · TT.MM.JJJJ</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-what"} -->
			<p class="tod-date-what">Noch eine Nacht</p>
			<!-- /wp:paragraph -->

			<!-- wp:paragraph {"className":"tod-date-where"} -->
			<p class="tod-date-where">Venue · Ort</p>
			<!-- /wp:paragraph -->
		</div>
		<!-- /wp:group -->
	</div>
	<!-- /wp:group -->

	<!-- wp:paragraph {"className":"h-note"} -->
	<p class="h-note">Neues Date: eine Zeile duplizieren (⋮ → Duplizieren), Texte tauschen. Vergangene Nächte einfach löschen — oder stehen lassen, als Archiv.</p>
	<!-- /wp:paragraph -->
</section>
<!-- /wp:group -->
