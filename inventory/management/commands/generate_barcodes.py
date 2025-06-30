from django.core.management.base import BaseCommand
from inventory.models import Product
from inventory.utils import generate_barcode
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate barcodes for products that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate barcodes for all products',
        )
        parser.add_argument(
            '--product-id',
            type=int,
            help='Generate barcode for specific product ID',
        )

    def handle(self, *args, **options):
        force = options['force']
        product_id = options.get('product_id')
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                products = [product]
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Product with ID {product_id} not found')
                )
                return
        else:
            if force:
                products = Product.objects.filter(is_active=True)
            else:
                products = Product.objects.filter(is_active=True, barcode__isnull=True)
        
        generated_count = 0
        
        for product in products:
            if not product.barcode or force:
                # Generate barcode using SKU
                barcode_data = product.sku
                
                try:
                    barcode_file = generate_barcode(barcode_data, product.name)
                    if barcode_file:
                        # Save barcode to product
                        product.barcode = barcode_data
                        product.save()
                        
                        generated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Generated barcode for {product.name} ({product.sku})'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Failed to generate barcode for {product.name}'
                            )
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error generating barcode for {product.name}: {str(e)}'
                        )
                    )
                    logger.error(f'Barcode generation error for {product.name}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {generated_count} barcodes'
            )
        )