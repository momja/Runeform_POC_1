from .models import Archetype, ElementType, Rect, Zone

CANVAS_W = 1080
CANVAS_H = 1080
M = 60  # margin

ARCHETYPES: list[Archetype] = [
    Archetype(
        name="hero_left_text_right",
        label="Hero Left, Text Right",
        zones=[
            Zone(
                name="hero",
                bounds=Rect(x=M, y=M, width=500, height=960),
                visual_weight=1.0,
                allowed_elements=[ElementType.HERO],
            ),
            Zone(
                name="headline",
                bounds=Rect(x=600, y=M, width=420, height=140),
                visual_weight=0.9,
                allowed_elements=[ElementType.HEADLINE],
            ),
            Zone(
                name="subhead",
                bounds=Rect(x=600, y=220, width=420, height=80),
                visual_weight=0.5,
                allowed_elements=[ElementType.SUBHEAD],
            ),
            Zone(
                name="body",
                bounds=Rect(x=600, y=340, width=420, height=300),
                visual_weight=0.4,
                allowed_elements=[ElementType.BODY],
            ),
            Zone(
                name="logo",
                bounds=Rect(x=600, y=880, width=140, height=140),
                visual_weight=0.3,
                allowed_elements=[ElementType.LOGO],
            ),
        ],
    ),
    Archetype(
        name="hero_full_overlay",
        label="Full Hero with Text Overlay",
        zones=[
            Zone(
                name="hero",
                bounds=Rect(x=0, y=0, width=CANVAS_W, height=CANVAS_H),
                visual_weight=1.0,
                allowed_elements=[ElementType.HERO],
            ),
            Zone(
                name="headline",
                bounds=Rect(x=M, y=680, width=700, height=140),
                visual_weight=0.9,
                allowed_elements=[ElementType.HEADLINE],
            ),
            Zone(
                name="subhead",
                bounds=Rect(x=M, y=830, width=500, height=60),
                visual_weight=0.5,
                allowed_elements=[ElementType.SUBHEAD],
            ),
            Zone(
                name="body",
                bounds=Rect(x=M, y=900, width=500, height=120),
                visual_weight=0.4,
                allowed_elements=[ElementType.BODY],
            ),
            Zone(
                name="logo",
                bounds=Rect(x=880, y=M, width=140, height=140),
                visual_weight=0.3,
                allowed_elements=[ElementType.LOGO],
            ),
        ],
    ),
    Archetype(
        name="hero_top_text_bottom",
        label="Hero Top, Text Bottom",
        zones=[
            Zone(
                name="hero",
                bounds=Rect(x=M, y=M, width=960, height=520),
                visual_weight=1.0,
                allowed_elements=[ElementType.HERO],
            ),
            Zone(
                name="headline",
                bounds=Rect(x=M, y=620, width=700, height=120),
                visual_weight=0.9,
                allowed_elements=[ElementType.HEADLINE],
            ),
            Zone(
                name="subhead",
                bounds=Rect(x=M, y=750, width=500, height=60),
                visual_weight=0.5,
                allowed_elements=[ElementType.SUBHEAD],
            ),
            Zone(
                name="body",
                bounds=Rect(x=M, y=830, width=500, height=130),
                visual_weight=0.4,
                allowed_elements=[ElementType.BODY],
            ),
            Zone(
                name="logo",
                bounds=Rect(x=860, y=860, width=140, height=140),
                visual_weight=0.3,
                allowed_elements=[ElementType.LOGO],
            ),
        ],
    ),
    Archetype(
        name="split_diagonal",
        label="Diagonal Split",
        zones=[
            Zone(
                name="hero",
                bounds=Rect(x=M, y=M, width=960, height=480),
                visual_weight=1.0,
                allowed_elements=[ElementType.HERO],
            ),
            Zone(
                name="headline",
                bounds=Rect(x=400, y=560, width=580, height=140),
                visual_weight=0.9,
                allowed_elements=[ElementType.HEADLINE],
            ),
            Zone(
                name="subhead",
                bounds=Rect(x=400, y=710, width=580, height=60),
                visual_weight=0.5,
                allowed_elements=[ElementType.SUBHEAD],
            ),
            Zone(
                name="body",
                bounds=Rect(x=400, y=790, width=580, height=150),
                visual_weight=0.4,
                allowed_elements=[ElementType.BODY],
            ),
            Zone(
                name="logo",
                bounds=Rect(x=M, y=800, width=160, height=160),
                visual_weight=0.3,
                allowed_elements=[ElementType.LOGO],
            ),
        ],
    ),
    Archetype(
        name="centered_stack",
        label="Centered Stack",
        zones=[
            Zone(
                name="logo",
                bounds=Rect(x=440, y=M, width=200, height=100),
                visual_weight=0.3,
                allowed_elements=[ElementType.LOGO],
            ),
            Zone(
                name="headline",
                bounds=Rect(x=140, y=180, width=800, height=160),
                visual_weight=0.9,
                allowed_elements=[ElementType.HEADLINE],
            ),
            Zone(
                name="hero",
                bounds=Rect(x=190, y=370, width=700, height=400),
                visual_weight=1.0,
                allowed_elements=[ElementType.HERO],
            ),
            Zone(
                name="subhead",
                bounds=Rect(x=240, y=800, width=600, height=60),
                visual_weight=0.5,
                allowed_elements=[ElementType.SUBHEAD],
            ),
            Zone(
                name="body",
                bounds=Rect(x=240, y=880, width=600, height=120),
                visual_weight=0.4,
                allowed_elements=[ElementType.BODY],
            ),
        ],
    ),
]
