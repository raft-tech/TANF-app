from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from django.db.models import Max

DOCUMENTS = [
      tanf.TANF_T1DataSubmissionDocument, tanf.TANF_T2DataSubmissionDocument,
      tanf.TANF_T3DataSubmissionDocument, tanf.TANF_T4DataSubmissionDocument,
      tanf.TANF_T5DataSubmissionDocument, tanf.TANF_T6DataSubmissionDocument,
      tanf.TANF_T7DataSubmissionDocument,

      ssp.SSP_M1DataSubmissionDocument, ssp.SSP_M2DataSubmissionDocument, ssp.SSP_M3DataSubmissionDocument,
      ssp.SSP_M4DataSubmissionDocument, ssp.SSP_M5DataSubmissionDocument, ssp.SSP_M6DataSubmissionDocument,
      ssp.SSP_M7DataSubmissionDocument,

      tribal.Tribal_TANF_T1DataSubmissionDocument, tribal.Tribal_TANF_T2DataSubmissionDocument,
      tribal.Tribal_TANF_T3DataSubmissionDocument, tribal.Tribal_TANF_T4DataSubmissionDocument,
      tribal.Tribal_TANF_T5DataSubmissionDocument, tribal.Tribal_TANF_T6DataSubmissionDocument,
      tribal.Tribal_TANF_T7DataSubmissionDocument
      ]

def count_all_records():
        """Count total number of records in the database."""
        total_num_records = 0
        for doc in DOCUMENTS:
            model = doc.Django.model
            total_num_records += model.objects.all().count()
        return total_num_records

def get_latest_meta_model():
      """Get the ReparseMeta model with the greatest pk."""
      max_pk = ReparseMeta.objects.all().aggregate(Max('pk'))
      return ReparseMeta.objects.get(pk=max_pk["pk__max"])
