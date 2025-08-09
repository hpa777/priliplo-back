from django.db.models import F
from django_cron import CronJobBase, Schedule
from time import gmtime, strftime
from datetime import datetime, date, timedelta
from django.utils.timezone import get_current_timezone
from company.models import Advertiser, Campaign, Billing_history, AdvertiserSettings, CampaignBalanceHistory
from client.models import ClientBalanceHistory, CampaignApplication, UserProfile, PhotoReport
from webpush import send_user_notification

# Отправить пуш уведомление о необходимости отправить фотоотчет
# python manage.py runcrons "priliplo.cron.PhotoReportsRequest"
class PhotoReportsRequest(CronJobBase):
    RUN_AT_TIMES = ['10:00']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'priliplo.photo_reports_request'

    def do(self):
        # print("-----------PhotoReportsRequest----------------")
        # today = datetime.now(tz=get_current_timezone())
        period_days_14 = timedelta(days=14)
        period_days_28 = timedelta(days=28)
        period_days_42 = timedelta(days=42)
        period_days_56 = timedelta(days=56)
        period_days_70 = timedelta(days=70)
        period_days_84 = timedelta(days=84)

        need_dates = [
            [(datetime.now(tz=get_current_timezone()) - period_days_14).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_14).replace(hour=23, minute=59, second=59, microsecond=0)],
            [(datetime.now(tz=get_current_timezone()) - period_days_28).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_28).replace(hour=23, minute=59, second=59, microsecond=0)],
            [(datetime.now(tz=get_current_timezone()) - period_days_42).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_42).replace(hour=23, minute=59, second=59, microsecond=0)],
            [(datetime.now(tz=get_current_timezone()) - period_days_56).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_56).replace(hour=23, minute=59, second=59, microsecond=0)],
            [(datetime.now(tz=get_current_timezone()) - period_days_70).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_70).replace(hour=23, minute=59, second=59, microsecond=0)],
            [(datetime.now(tz=get_current_timezone()) - period_days_84).replace(hour=0, minute=0, second=0, microsecond=0), (datetime.now(tz=get_current_timezone()) - period_days_84).replace(hour=23, minute=59, second=59, microsecond=0)],
        ]
        # print (need_dates)
        for arr in need_dates:
            campaign_application = CampaignApplication.objects.filter(application_status=2).filter(edited_date__range=(arr[0], arr[1])).all()
            # campaign_application = CampaignApplication.objects.filter(edited_date__range=(arr[0], arr[1])).all()
            for application in campaign_application:
                send_user_notification(user=application.client, payload={"head": "Фотоотчеты", "body": "Вам необходимо отправить фотоотчет в сервисе priliplo.ru!", "url": "https://lk.priliplo.ru"}, ttl=1000)


class PhotoReportsAccept(CronJobBase):
    RUN_AT_TIMES = ['03:20']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'priliplo.photo_reports_accept'

    def do(self):
        # выбрать все отчеты которые лежат больше 3 дней в статусе "на рассмотрении"
        period_3_days = timedelta(days=3)
        today = datetime.now(tz=get_current_timezone()) - period_3_days
        photoreports = PhotoReport.objects.filter(photoreport_status=1).filter(edited_date__lte=today).all()
        for photoreport in photoreports:
            # принять отчет
            photoreport.accept()

class CampaignCronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RUN_AT_TIMES = ['03:30']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    # schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'priliplo.campaign_cron_job'  # a unique code

    def do(self):
        # Выборка всех кампаний завершающихся сегодня
        try:
            # campaign_billing_period_90_days = timedelta(days=104)
            campaign_billing_period_90_days = timedelta(days=98) # 84 дня + 2 недели
            # today = datetime.now(tz=get_current_timezone()) + campaign_billing_period_90_days  # прибавить 3 месяца к дате одобрения акции
            # campaigns = Campaign.objects.filter(campaign_status=2).filter(end_date__lte=today).all()
            today = datetime.now(tz=get_current_timezone())
            print ("TODAY", today)
            # print ("(campaign.end_date + campaign_billing_period_90_days)", (Campaign.objects.filter(campaign_status=2).first().end_date + campaign_billing_period_90_days))
            # campaigns = Campaign.objects.filter(campaign_status=2).all()
            campaigns = Campaign.objects.filter(campaign_status=2).filter(end_date__lte=today).all()
            for campaign in campaigns:
                if (campaign.end_date + campaign_billing_period_90_days) < today:
                    advertiser = campaign.advertiser
                    campaign_award = campaign.award

                    # Выбрать какая квота у кампании
                    print(campaign)
                    # сколько автомобилей реально участвует
                    active_applications = CampaignApplication.objects.filter(campaign=campaign).filter(application_status=2).all()
                    # print("--", active_applications)


                    # Возврат не использованных денег на баланс
                    billing_history_object = Billing_history.objects.create(advertiser=advertiser, balance_increase=campaign.campaign_balance, change_type=5)

                    # campaign.campaign_balance = 0
                    campaign.campaign_status = 4  # Пометка кампании как завершенной
                    campaign.save()

                    campaign_balance_history_object = CampaignBalanceHistory.objects.create(advertiser=advertiser, campaign=campaign, balance_decrease=campaign.campaign_balance, change_type=4)

                    # cashback = campaign.quota - active_applications.count()

                    # Клиентам участвующим в акции закинуть баллы на баланс
                    # for application in active_applications:
                    #     client_balance_history = ClientBalanceHistory.objects.create(
                    #         client=application.client,
                    #         campaign=campaign,
                    #         advertiser=advertiser,
                    #         balance_increase=campaign_award,
                    #         change_type=3
                    #     )

                    # Заявки клиентов участвующие в акции пометить как завершенные
                    active_applications.update(application_status=7)
            # ClientBalanceHistory.objects.filter(pk=instance.pk).update(balance_current=current_balance)

            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            print("campaign_cron_job")
            return "OK at " + strftime("%Y-%m-%d %H:%M:%S", gmtime())
        except:
            print("campaign_cron_job except")
            return "ERROR"
        # print(campaigns)
        # docker exec -t priliplo_web python /code/manage.py runcrons
        # */1 * * * * docker exec -t priliplo_web python /code/manage.py runcrons > /root/project/priliplo_cronjob.log


# Функция для списания денег каждый месяц
class ClientBalanceCronJob(CronJobBase):
    RUN_AT_TIMES = ['03:40']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'priliplo.client_balance_cron_job' # a unique code

    def do(self):
        advertiser_settings = AdvertiserSettings.objects.first()

        today = datetime.now(tz=get_current_timezone()).date()
        campaign_billing_period_1 = timedelta(days=30)
        campaign_billing_period_2 = timedelta(days=60)
        campaign_billing_period_3 = timedelta(days=90)

        campaigns = Campaign.objects.filter(campaign_status=2).all()
        print("ClientBalanceCronJob")
        for campaign in campaigns:
            # print(campaign.approve_date)
            # print(campaign.approve_date + campaign_billing_period_1)
            # print(campaign.approve_date + campaign_billing_period_2)
            # print(campaign.approve_date + campaign_billing_period_3)
            # каждый период списывать с баланса кампании деньги за пройденный период
            if today == (campaign.approve_date + campaign_billing_period_1) or today == (campaign.approve_date + campaign_billing_period_2) or today == (campaign.approve_date + campaign_billing_period_3):
                # campaign.campaign_balance = F('campaign_balance') - advertiser_settings.period_cost
                # campaign.save()

                new_campaign_balance = campaign.campaign_balance - advertiser_settings.period_cost
                campaign_balance_history_object = CampaignBalanceHistory.objects.create(advertiser=campaign.advertiser, campaign=campaign, balance_decrease=new_campaign_balance, change_type=5)
                # campaign.update(campaign_balance=(F('campaign_balance')-advertiser_settings.period_cost))
        return "ClientBalanceCronJob OK"
