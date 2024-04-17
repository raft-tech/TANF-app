from .models import ParserErrorCategoryChoices

class ErrorPrecedence:
    def __init__(self):
        self.max_precedence = None

    def has_precedence(self, error_level):
        """Returns tuple of bools: (has_precidence, is_new_max_precedence)."""
        if self.max_precedence is None:
            self.max_precedence = error_level
            return (True, True)
        elif self.max_precedence > error_level:
            self.max_precedence = error_level
            return (True, True)
        elif self.max_precedence == error_level:
            return (True, False)
        else:
            return (False, False)


class CaseHashtainer:
    def __init__(self, my_hash, CASE_NUMBER, RPT_MONTH_YEAR, manager_error_dict, generate_error):
        self.my_hash = my_hash
        self.CASE_NUMBER = CASE_NUMBER
        self.RPT_MONTH_YEAR = RPT_MONTH_YEAR
        self.manager_error_dict = manager_error_dict
        self.generate_error = generate_error
        self.record_ids = set()
        self.record_hashes = dict()
        self.partial_hashes = dict()
        self.error_precedence = ErrorPrecedence()

    def __generate_error(self, err_msg, is_new_max_precedence):
        if err_msg is not None:
            error = self.generate_error(
                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                        schema=None, ## TODO: Do we need the right schema? Can this be None to avoid so much state?
                        record=None,
                        field=None,
                        error_message=err_msg,
                    )
            if is_new_max_precedence:
                self.manager_error_dict[self.my_hash] = [error]
            else:
                self.manager_error_dict[self.my_hash].append(error)

    def add_case_member(self, record, line, line_number):
        self.record_ids.add(record.id)
        line_hash = hash(line)
        partial_hash = None
        error_level = record.RecordType[1]
        if record.RecordType == "T1":
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        else:
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER + str(record.FAMILY_AFFILIATION) + record.DATE_OF_BIRTH + record.SSN)

        is_exact_dup = False
        err_msg = None
        has_precedence = False
        is_new_max_precedence = False

        if line_hash in self.record_hashes:
            has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(error_level)
            existing_record_id, existing_record_line_number = self.record_hashes[line_hash]
            err_msg = (f"Duplicate record detected for record id {record.id} with record type {record.RecordType} at "
                               f"line {line_number}. Record is a duplicate of the record at line number "
                               f"{existing_record_line_number}, with record id {existing_record_id}")
            is_exact_dup = True

        skip_partial = False
        if  record.RecordType != "T1":
            skip_partial = record.FAMILY_AFFILIATION == 3 or record.FAMILY_AFFILIATION == 5
        if not skip_partial and not is_exact_dup and partial_hash in self.partial_hashes:
            has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(error_level)
            err_msg = (f"Partial duplicate record detected for record id {record.id} with record type {record.RecordType} at "
                               f"line {line_number}. Record is a partial duplicate of the record at line number "
                               f"{self.partial_hashes[partial_hash][1]}, with record id {self.partial_hashes[partial_hash][0]}")
        
        if not has_precedence:
            err_msg = None
        
        self.__generate_error(err_msg, is_new_max_precedence)
        if line_hash not in self.record_hashes:
            self.record_hashes[line_hash] = (record.id, line_number)
        if partial_hash not in self.partial_hashes:
            self.partial_hashes[partial_hash] = (record.id, line_number)


class RecordDuplicateManager:

    def __init__(self, generate_error):
        self.hashtainers = dict()
        self.generate_error = generate_error
        self.generated_errors = dict()

    def add_record(self, record, line, line_number):
        hash_val = hash(str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        if hash_val not in self.hashtainers:
            hashtainer = CaseHashtainer(hash_val, record.CASE_NUMBER, str(record.RPT_MONTH_YEAR), 
                                        self.generated_errors, self.generate_error)
            self.hashtainers[hash_val] = hashtainer
        self.hashtainers[hash_val].add_case_member(record, line, line_number)

    def get_generated_errors(self):
        generated_errors = list()
        for errors in self.generated_errors.values():
            generated_errors.extend(errors)
        return generated_errors
