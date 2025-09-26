from django.urls import path, re_path
from django.views.generic.list_detail import object_detail, object_list

from repository.models import ClinicalTrial

from repository.views import edit_trial_index, full_view, index, step_1, step_2, step_3
from repository.views import step_4, step_5, step_6, step_7, step_8, step_9, new_institution
from repository.views import trial_registered, trial_view, recruiting, trial_ictrp, trial_otxml
from repository.views import all_trials_ictrp, contacts, advanced_search, multi_otxml, custom_otcsv


urlpatterns = [
    path('edit/<int:trial_pk>/', edit_trial_index, name='repository.edittrial'),
    path('view/<int:trial_pk>/', trial_view, name='repository.trialview'),
    path('new_institution/', new_institution, name='new_institution'),
    path('contacts/', contacts, name='contacts'),
    path('step_1/<int:trial_pk>/', step_1, name='step_1'),
    path('step_2/<int:trial_pk>/', step_2, name='step_2'),
    path('step_3/<int:trial_pk>/', step_3, name='step_3'),
    path('step_4/<int:trial_pk>/', step_4, name='step_4'),
    path('step_5/<int:trial_pk>/', step_5, name='step_5'),
    path('step_6/<int:trial_pk>/', step_6, name='step_6'),
    path('step_7/<int:trial_pk>/', step_7, name='step_7'),
    path('step_8/<int:trial_pk>/', step_8, name='step_8'),
    path('step_9/<int:trial_pk>/', step_9, name='step_9'),
    # public
    path('recruiting/', recruiting, name='repository.recruiting'),
    path('advanced_search/', advanced_search, name='repository.advanced_search'),
    path('<slug:trial_fossil_id>/', trial_registered, name='repository.trial_registered'),
    path('<slug:trial_fossil_id>/xml/ictrp/', trial_ictrp, name='repository.trial_ictrp'),
    path('<slug:trial_fossil_id>/xml/ot/', trial_otxml, name='repository.trial_otxml'),
    path('<slug:trial_fossil_id>/v<int:trial_version>/', trial_registered, name='repository.trial_registered_version'),
    path('<slug:trial_fossil_id>/v<int:trial_version>/xml/ictrp/', trial_ictrp, name='repository.trial_ictrp_version'),
    path('<slug:trial_id>/v<int:trial_version>/xml/opentrials/', trial_otxml, name='repository.trial_otxml_version'),
    path('all/xml/ictrp', all_trials_ictrp),
    re_path(r'^multi/xml/ot', multi_otxml, name='repository.multi_otxml'),
    re_path(r'^multi/csv/ot', custom_otcsv, name='repository.custom_otcsv'),
    path('', index, name='repository.index'),
]
