import typing
import numpy as np
import pandas as pd
from enum import Enum

"""
This script will look through the assets csv and account csv files.
The assets csv will contain the assets that are in distributor inventory or
in distributor owned accounts.
The accounts csv will contain the accounts that are distributors or
distributor owned accounts.
"""


class AccountTypes(Enum):
    """
    Enum of account categories in Salesforce maps the name to index in accounts CSV
    """
    DISTRIBUTOR = "Distributor"
    END_USER = "End-User"
    ROBOT_OEM = "Robot OEM"
    INTEGRATOR = "Robot Integrator"
    RESEARCH_EDU = "Research + Edu"
    TECHNOLOGY_SOLUTION_PROVIDER = "Technology Solution Provider"
    GRANT = "Grant"
    INTERNAL = "Internal"
    VC_VCV = "VC-VCV"


def _index_find(name: str, arr: np.ndarray) -> int:
    return np.where(arr[0] == name)[0][0]


class AccountsAndAssets:
    """
    Contains the account csv file information and can retrieve information in different formats.
    """

    def __init__(self, accounts_file_name: str, assets_file_name: str):
        """
        Constructor for the class that requires queried CSV files from Dataloader.io
        :param accounts_file_name: the account CSV file query name as a string
        :param assets_file_name: the assets CSV file query name as a string
        """
        try:
            self._accounts_arr = np.genfromtxt(accounts_file_name, delimiter=',', dtype=str)
        except IOError:
            raise Exception("Accounts file not found.")

        if len(self._accounts_arr) < 2:
            raise Exception("Accounts file is empty")

        assets_df = pd.read_csv(assets_file_name)
        assets_header = assets_df.columns.tolist()
        try:
            self._assets_arr = assets_df.fillna('').to_numpy()
            self._assets_arr = np.vstack((assets_header, self._assets_arr))

        except IOError:
            raise Exception("Assets file not found.")

        if len(self._assets_arr) < 2:
            raise Exception("Assets file is empty.")

        # print("assets array: \n", self._assets_arr)
        # The indices for different cols of the accounts file
        self._accounts_category_index = _index_find('Category__c', self._accounts_arr)
        self._accounts_id_index = _index_find('Id', self._accounts_arr)
        self._accounts_partner_owner_index = _index_find('Partner_Owner__c', self._accounts_arr)

        # The indices for different cols of the assets file
        self._asset_account_name = _index_find('Account.Name', self._assets_arr)
        self._asset_account_partner_owner = _index_find('Account.Partner_Owner__c', self._assets_arr)
        self._asset_account_id = _index_find('AccountId', self._assets_arr)
        self._asset_id = _index_find('Id', self._assets_arr)

    """
    Account file methods
    """
    @property
    def get_account_arr(self) -> np.ndarray:
        """
        Gets the private class member account array that holds the information passed from the accounts CSV file
        :return: the private class member accounts array
        """
        return self._accounts_arr

    def get_accounts_by_type(self, account_type: AccountTypes) -> typing.List[str]:
        """
        Gets all accounts pertaining to the passed account category.
        :param account_type: the category of the accounts to be queried
        :return:  a list of strings that holds all the ids that are of the given account category
        """
        return [row[self._accounts_id_index] for row in self._accounts_arr if row[self._accounts_category_index] == account_type.value]

    def get_account_ids(self) -> typing.List[str]:
        """
        Gets all the account ids from the assets file. These include all end-users and distributors.
        :return: a list of strings that holds all the ids of all the accounts
        """
        return [row[self._accounts_id_index] for row in self._accounts_arr[1:]]

    def get_distributor_and_child(self, distributor_id: str) -> typing.List[str]:
        """
        Gets the child accounts for a given distributor, given the distributor id
        :param distributor_id: the id that pertains to the distributor to get the child accounts from
        :return: a list of strings that holds the ids of the child accounts that belong to the given distributor
        """
        return [row.tolist() for row in self._accounts_arr if row[self._accounts_partner_owner_index] == distributor_id]

    def get_distributor_of_end_user(self, end_user_id: str) -> str:
        """
        Gets the distributor of a given end user id
        :param end_user_id: the id pertaining to the end user
        :return: the corresponding distributor id, as a string, for the end user
        """
        account_ids = np.array(self.get_account_ids())
        end_user_index = np.where(account_ids == end_user_id)
        distributor_id = self._accounts_arr[end_user_index[0][0] + 1][self._accounts_partner_owner_index]
        if distributor_id is None:
            raise (Exception, "Id entered does not pertain to an end-user.")

        return distributor_id

    """
    Assets file methods
    """
    @property
    def get_assets_arr(self) -> np.ndarray:
        """
        Gets the assets array made from the assets CSV file.
        :return: private class member assets array
        """
        return self._assets_arr

    def get_assets_by_account_id(self, account_id: str) -> typing.List[str]:
        """
        Gets all asset ids, as a list of strings, that belong to a given account
        :param account_id: the id of the account to get the assets from
        :return: a list of strings with all the asset ids that belong to the given account
        """
        return [row for row in self._assets_arr if row[self._asset_id] == account_id]

    def get_all_assets_by_distributor(self, distributor_id: str) -> typing.List[str]:
        """
        Gets all the asset ids given a distributor id
        :param distributor_id: the id corresponding to the distributor to get the assets from
        :return: a list of strings that holds all the asset ids that belong to the given distributor
        """
        distributor_ids = self.get_accounts_by_type(AccountTypes.DISTRIBUTOR)
        if distributor_id not in distributor_ids:
            print('ID [', distributor_id, '] does not pertain to a distributor.')

        distributor_children = self.get_distributor_and_child(distributor_id)
        distributor_children_ids = [row[self._accounts_id_index] for row in distributor_children]
        result = [row.tolist() for row in self._assets_arr if (row[self._asset_account_id] in distributor_children_ids
                                                               or row[self._asset_account_partner_owner] ==
                                                               distributor_id or row[self._asset_account_id] ==
                                                               distributor_id)]
        return result

    def split_assets_by_distributor(self) -> typing.Dict[str, np.ndarray]:
        """
        Divides the all assets from all distributors file into
        :return:
        """
        distributor_ids = self.get_accounts_by_type(AccountTypes.DISTRIBUTOR)
        array_dict = {}
        for distributor_id in distributor_ids:
            new_file_arr = self.get_all_assets_by_distributor(distributor_id)
            if len(new_file_arr) > 0:
                new_file_arr = np.vstack([self._assets_arr[0], new_file_arr])  # stack parameter name row on top of file
                array_dict[distributor_id] = new_file_arr
            else:
                print('Distributor [', distributor_id, '] does not have any assets.')

        return array_dict

    def split_assets_and_save_csv(self):
        file_dict = self.split_assets_by_distributor()
        for key, value in file_dict.items():
            np.savetxt(key + '.csv', value, delimiter=',', fmt=('%s'))


class CombinedFiles:
    """
    Class for combining files that distributor has updated based on their inventory changes.
    Adding files to the class will insert a new entry into the changed files dictionary, which will contain the files
    from different distributors and their corresponding ids.
    The dictionary entries can then be written to one file that is ready to upload to Salesforce.
    """
    def __init__(self, accounts_file_name: str, original_all_assets_name: str):
        """
        Constructor for CombinedFiles class.
        :param accounts_file_name: the original accounts file name (before splitting and sending to distributor)
        with all the distributor accounts and their child accounts.
        :param original_all_assets_name: the original assets file name (before splitting and sending to distributor)
        that contains information on all assets that are under a distributor (in their inventory) or under one of
        their child accounts.
        """
        self._files = {}  # files dictionary
        # AccountAndAssets private object to keep track and utilize the original files (compare, verify, etc.)
        self._original_accounts_and_assets = AccountsAndAssets(accounts_file_name, original_all_assets_name)
        self.combined_arr = []
        self.changes =[]
        self.accountIdIndex = _index_find("AccountId", self._original_accounts_and_assets.get_assets_arr)

    @property
    def get_files(self) -> typing.Dict[str, str]:
        return self._files

    @property
    def get_combined_list(self) -> typing.List[str]:
        return self.combined_arr

    def add_file(self, file_name: str):
        """
        Adds a new entry to the dictionary.
        :param file_name: name of the file to look for and insert contents into dictionary.
        :return: None
        """
        try:
            f_dataframe = pd.read_csv(file_name)
        except IOError:
            raise Exception("Assets file not found.")

        f_header = f_dataframe.columns.tolist()
        f = f_dataframe.fillna('').to_numpy()
        f = np.vstack((f_header, f))

        if len(f) < 2:
            raise Exception("Assets file is empty.")

        self._files[file_name] = f.tolist()  # key -> file name; value -> file contents

    def combine_files(self):
        """
        Combines all the entries in the dictionary and writes the appended file.
        :return: None
        """
        if len(self._files) == 0:
            print("No files added.")

        temp = []
        header = list(self._files.values())[0][0]
        for key, value in self._files.items():
            if len(temp) == 0:
                temp = value[1:]
            else:
                temp = np.vstack((temp, value[1:]))

        self.combined_arr = np.vstack((header, temp)).tolist()

    def show_changes(self) -> typing.List[typing.List[str]]:
        """
        Shows the user the changes made by the distributor.
        :return: None
        """
        sorted_combined = sorted(self.combined_arr)
        sorted_original = sorted(self._original_accounts_and_assets.get_assets_arr.tolist())
        self.changes = [[row_original, row_combined] for row_combined, row_original in zip(sorted_combined, sorted_original) if row_combined != row_original]

        [print("original:\t\t\t\t", change[0], "\ndistributor change:\t\t", change[1]) for change in self.changes]
        return self.changes

    def get_inventory_change_number(self) -> int:
        """
        Returns the number of inventory changes (Asset account ID changes or distributor sales) occurred.
        :return: The number of changes.
        """
        if not self.changes:
            print("No changes made or file has not been combined.")
        count = 0
        for change in self.changes:
            if change[0][self.accountIdIndex] != change[1][self.accountIdIndex]:
                count += 1

        return count

    def write_combined_file(self):
        if not self.combined_arr:
            print("Empty combined array. Add files to combine.")
            return

        df = pd.DataFrame(self.combined_arr)
        df.to_csv('combined_file.csv', header=False, index=False)

