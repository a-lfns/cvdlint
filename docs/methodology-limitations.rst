Methodology and limitations
===========================

For each palette, ``cvdlint``:

#. parses explicit sRGB colours;
#. simulates protanopia, deuteranopia, and tritanopia using the
   full-dichromacy matrices from Machado, Oliveira, and Fernandes (2009);
#. converts the normal and simulated colours to CIE Lab;
#. calculates pairwise CIEDE2000, CIE94, or CIE76 differences; and
#. reports pairs below the selected tolerance.

What a result means
-------------------

A finding is a warning about potential confusion under a mathematical model,
not a guarantee about every observer or display. Simulated RGB values are
model-specific approximations and may differ from applications that use
another model. Distance thresholds are policy choices rather than universal
accessibility pass marks.

Colour is also only one part of accessible visual design. Important categories
should use redundant cues such as labels, line styles, markers, patterns, or
position where practical. Human review remains valuable, particularly for
small marks, low contrast, transparency, and colours shown against different
backgrounds.

Static and runtime coverage
---------------------------

Static linting is deterministic and safe for routine CI because it never runs
the target project. Its cost is that dynamically generated colours are outside
its knowledge. Runtime checks can inspect the resulting palette or figure, but
they must execute the user's code and therefore inherit its dependencies,
required data, credentials, network access, and possible side effects.

Acknowledgements
----------------

The palette-analysis API and original relative-tolerance policy were informed
by Jakub Nowosad's R package `colorblindcheck
<https://github.com/Nowosad/colorblindcheck>`_. Its published results are used
as compatibility references. ``cvdlint`` is an independent Python
implementation with its own static-linting and reporting features.
