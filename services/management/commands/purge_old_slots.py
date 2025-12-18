# services/management/commands/purge_old_slots.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from services.models import AppointmentSlot, Reservation

class Command(BaseCommand):
    help = "Expire old reservations and purge/archive past appointment slots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would happen without changing the database.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        today = timezone.localdate()

        # 1) expire رزروهای گذشته که هنوز نهایی نشده‌اند
        with transaction.atomic():
            pending_qs = Reservation.objects.filter(
                slot__date__lt=today,
                status__in=[Reservation.Status.DRAFT, Reservation.Status.PENDING],
            )
            pending_count = pending_qs.count()
            if dry_run:
                self.stdout.write(self.style.WARNING(f"[DRY] Will EXPIRE reservations: {pending_count}"))
            else:
                updated = pending_qs.update(status=Reservation.Status.EXPIRED, updated_at=timezone.now())
                self.stdout.write(self.style.WARNING(f"Expired old reservations: {updated}"))

        # 2) حذف اسلات‌های گذشته که رزرو فعال (pending/booked) ندارند
        with transaction.atomic():
            empty_old = (
                AppointmentSlot.objects
                .filter(date__lt=today)
                .annotate(active_res=Count('reservations',
                    filter=Q(reservations__status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED])))
                .filter(active_res=0)
            )
            empty_count = empty_old.count()
            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY] Will DELETE empty past slots: {empty_count}"))
            else:
                deleted_count, _ = empty_old.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted empty past slots: {deleted_count}"))

        # 3) آرشیو اسلات‌های گذشته که رزرو فعال دارند
        with transaction.atomic():
            archivable = (
                AppointmentSlot.objects
                .filter(date__lt=today)
                .annotate(active_res=Count('reservations',
                    filter=Q(reservations__status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED])))
                .filter(active_res__gt=0)
            )
            arch_count = archivable.count()
            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY] Will ARCHIVE past slots (with active reservations): {arch_count}"))
            else:
                archived = archivable.update(is_archived=True)
                self.stdout.write(self.style.SUCCESS(f"Archived past slots: {archived}"))

        self.stdout.write(self.style.SUCCESS("Cleanup finished."))
