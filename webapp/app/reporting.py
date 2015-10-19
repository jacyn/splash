import json
import sys

from app import models as app_models


class SurveyReport(object):

    @classmethod
    def generate(self, context, surveys=None, revision_id=0, date_from=None, date_to=None):
        all_survey_revisions_set = set()

        survey_reports = { }
        for survey in surveys:
            survey_revisions = survey.revisions.all().order_by("revision_no")
            if revision_id:
                survey_revisions = survey_revisions.filter(pk=revision_id)

            for revision in survey_revisions:
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
                        value = survey_answers.get(code, None)
                        if isinstance(value, list):
                            value = ", ".join(value)
                        line.append(value)

                    data.append(line)

                survey_reports[revision.pk] = dict()
                survey_reports[revision.pk]["headers"] = [ "ID", "Date/Time Added", ] + [str(v) for k, v in survey_questions.items()]
                survey_reports[revision.pk]["data"] = data

        for sr in all_survey_revisions_set:
            sr.report = survey_reports[sr.pk]

        context.update({
            "reports": all_survey_revisions_set,
        })

