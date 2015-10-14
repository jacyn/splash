import json
import sys

from app import models as app_models


class SurveyReport(object):

    @classmethod
    def generate(self, context, surveys=None, date_from=None, date_to=None):
        all_survey_revisions_set = set()

        survey_reports = { }
        for survey in surveys:
            for revision in survey.revisions.all().order_by("revision_no"):
                all_survey_revisions_set.add(revision)
                survey_questions = json.loads(revision.questions)
                questions = [str(v) for k, v in survey_questions.items()]

                data = [ ]
                for answer in revision.answers.all().order_by("-date_created"):
                    if answer.test_mode:
                        continue

                    survey_answers = json.loads(answer.answers)

                    line = [ answer.pk, answer.date_created, ]
                    for code in survey_questions.keys():
                        line.append(survey_answers.get(code, None))

                    data.append(line)

                survey_reports[revision.pk] = dict()
                survey_reports[revision.pk]["headers"] = [ "ID", "Date/Time Added", ] + [str(v) for k, v in survey_questions.items()]
                survey_reports[revision.pk]["data"] = data

        for sr in all_survey_revisions_set:
            sr.report = survey_reports[sr.pk]

        context.update({
            "reports": all_survey_revisions_set,
        })

