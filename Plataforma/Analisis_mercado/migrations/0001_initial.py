# Generated by Django 5.2 on 2025-04-03 09:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Habilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OfertaEmpleo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('empresa', models.CharField(max_length=255)),
                ('ubicacion', models.CharField(max_length=255)),
                ('salario', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fecha_publicacion', models.DateField()),
                ('plataforma', models.CharField(choices=[('tecnoempleo', 'Tecnoempleo'), ('infojobs', 'InfoJobs'), ('linkedin', 'LinkedIn')], max_length=50)),
                ('habilidades_requeridas', models.ManyToManyField(related_name='ofertas_habilidades', to='Analisis_mercado.habilidad')),
            ],
        ),
        migrations.CreateModel(
            name='TendenciaHabilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('cantidad_ofertas', models.PositiveIntegerField()),
                ('habilidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Analisis_mercado.habilidad')),
            ],
        ),
    ]
