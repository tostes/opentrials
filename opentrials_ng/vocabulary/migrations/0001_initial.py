from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("iso_code", models.CharField(max_length=2, unique=True)),
            ],
            options={
                "ordering": ["label"],
                "verbose_name": "Country",
                "verbose_name_plural": "Countries",
            },
        ),
        migrations.CreateModel(
            name="InstitutionType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "label"]},
        ),
        migrations.CreateModel(
            name="InterventionAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Intervention assignment",
                "verbose_name_plural": "Intervention assignments",
            },
        ),
        migrations.CreateModel(
            name="InterventionCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "label"]},
        ),
        migrations.CreateModel(
            name="ObservationalStudyDesign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Observational study design",
                "verbose_name_plural": "Observational study designs",
            },
        ),
        migrations.CreateModel(
            name="RecruitmentStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Recruitment status",
                "verbose_name_plural": "Recruitment statuses",
            },
        ),
        migrations.CreateModel(
            name="StudyAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Study allocation",
                "verbose_name_plural": "Study allocation",
            },
        ),
        migrations.CreateModel(
            name="StudyMasking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Study masking",
                "verbose_name_plural": "Study masking",
            },
        ),
        migrations.CreateModel(
            name="StudyPhase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Study phase",
                "verbose_name_plural": "Study phases",
            },
        ),
        migrations.CreateModel(
            name="StudyPurpose",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "label"]},
        ),
        migrations.CreateModel(
            name="StudyType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "label"]},
        ),
        migrations.CreateModel(
            name="TimePerspective",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "label"]},
        ),
        migrations.CreateModel(
            name="TrialNumberAuthority",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(blank=True, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order", "label"],
                "verbose_name": "Trial number issuing authority",
                "verbose_name_plural": "Trial number issuing authorities",
            },
        ),
    ]
