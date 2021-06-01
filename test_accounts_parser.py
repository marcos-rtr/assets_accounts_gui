import numpy as np
import pandas as pd
import typing
from unittest import TestCase
from accounts_parser import AccountsAndAssets, AccountTypes, CombinedFiles


def file_prep(df: pd.DataFrame) -> typing.List[str]:
    header = df.columns.tolist()
    result = df.fillna('').to_numpy()
    return sorted(np.vstack((header, sorted(result.tolist()))).tolist())


class TestAccountsAndAssets(TestCase):
    def setUp(self) -> None:
        self.accounts = AccountsAndAssets('distributors_and_children.csv', 'assets.csv')


class TestInitAndAssets(TestAccountsAndAssets):
    def __int__(self):
        self.maxDiff = None

    def test_constructor_accounts_fnf(self):
        self.assertRaises(Exception, AccountsAndAssets, 'bogusfile', 'assets.csv')

    def test_constructor_assets_fnf(self):
        self.assertRaises(Exception, AccountsAndAssets, 'bogusfile', 'assets.csv')

    def test_empty_file_account(self):
        self.assertRaises(Exception, AccountsAndAssets, 'empty.csv', 'assets.csv')

    def test_empty2_file_account(self):
        self.assertRaises(Exception, AccountsAndAssets, 'empty2.csv', 'assets.csv')

    def test_empty_file_assets(self):
        self.assertRaises(Exception, AccountsAndAssets, 'account.csv', 'empty.csv')

    def test_empty2_file_assets(self):
        self.assertRaises(Exception, AccountsAndAssets, 'accounts.csv', 'empty2.csv')

    def test_get_accounts_arr(self):
        expected = [
            ['Id', 'Description', 'Name', 'Category__c', 'Partner_Owner__c', 'Shipping_POC__c', 'Technical_POC__c'],
            ['0011U000008D4kPQAS', '', 'Aisin Group', 'End-User', '0011U000007zcnLQAQ', '', ''],
            ['0011U000008Dh2dQAC', '', 'Nexty', 'Distributor', '', '', ''],
            ['0011U00001N9EUHQA3', '', 'FFT', 'End-User', '0011U00000pT9FAQA0', '0031U00001covJXQAY',
             '0031U00001covJXQAY'],
            ['0011U000010Tr71QAC', '', 'Toyota Tsusho Corporation', 'Distributor', '', '', ''],
            ['0011U0000184CbxQAE', '', 'Buchanan Automation', 'Distributor', '', '', ''],
            ['0011U000010TqgQQAS', '', 'JOHNAN', 'Distributor', '', '', ''],
            ['0011U000007zcnLQAQ', 'Distributor', 'Johnan Corp', 'Distributor', '', '0031U00001JhhxIQAR',
             '0031U00001JhhxIQAR'],
            ['0011U00001HTapHQAT', '', 'Kantum Ushikata', 'Distributor', '', '', ''],
            ['0011U00001PONs4QAH', '', 'Tokyo University', 'Research + Edu', '0011U000007zcnLQAQ', '',
             '0031U00001JhhxIQAR'],
            ['0011U000007zcdGQAQ', '', 'Sony Electronics Inc', 'End-User', '0011U000007zcnLQAQ', '', '']]

        self.assertEqual(sorted(expected), sorted(self.accounts._accounts_arr.tolist()))

    def test_get_accounts_by_type(self):
        result = sorted(self.accounts.get_accounts_by_type(AccountTypes.DISTRIBUTOR))
        expected = sorted(['0011U000010TqgQQAS', '0011U000008Dh2dQAC', '0011U000010Tr71QAC', '0011U0000184CbxQAE',
                           '0011U000007zcnLQAQ', '0011U00001HTapHQAT'])

        self.assertEqual(expected, result)

    def test_get_account_ids(self):
        result = sorted(self.accounts.get_account_ids())
        expected = sorted(['0011U000008D4kPQAS',
                           '0011U000008Dh2dQAC',
                           '0011U00001N9EUHQA3',
                           '0011U000010Tr71QAC',
                           '0011U0000184CbxQAE',
                           '0011U000010TqgQQAS',
                           '0011U000007zcnLQAQ',
                           '0011U00001HTapHQAT',
                           '0011U00001PONs4QAH',
                           '0011U000007zcdGQAQ'])

        self.assertEqual(expected, result)

    def test_get_distributor_and_child_not_empty(self):
        result = sorted(self.accounts.get_distributor_and_child('0011U000007zcnLQAQ'))
        expected = sorted([['0011U000008D4kPQAS', '', 'Aisin Group', 'End-User', '0011U000007zcnLQAQ', '', ''],
                           ['0011U00001PONs4QAH', '', 'Tokyo University', 'Research + Edu', '0011U000007zcnLQAQ', '',
                            '0031U00001JhhxIQAR'],
                           ['0011U000007zcdGQAQ', '', 'Sony Electronics Inc', 'End-User',
                            '0011U000007zcnLQAQ', '', '']])
        self.assertEqual(expected, result)

    def test_get_distributor_and_child_empty(self):
        result = sorted(self.accounts.get_distributor_and_child('0011U000008D4kPQAS'))
        expected = sorted([])

        self.assertEqual(expected, result)

    def test_get_distributor_of_end_user_valid(self):
        result = self.accounts.get_distributor_of_end_user('0011U000008D4kPQAS')
        expected = '0011U000007zcnLQAQ'

        self.assertEqual(expected, result)

    def test_get_distributor_of_end_user_invalid(self):
        result = self.accounts.get_all_assets_by_distributor('0011U000007zcnLQAQ')

        self.assertRaises(Exception, result)

    def test_get_all_assets_by_distributor_valid(self):
        result = sorted(self.accounts.get_all_assets_by_distributor('0011U000007zcnLQAQ'))
        expected = sorted([['02i1U000000OEbrQAG', '0011U000007zcnLQAQ', 'MPA 0086', '', '', '2 2.1 0086',
                            '2 2.1 0086', '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000003mD2gQAE', '0011U000007zcnLQAQ', 'MPA 0254', '', '', 'RTR-MPA-0003-2038-0254',
                            'RTR-MPA-0003-2038-0254', '', 'Johnan Corp', ''],
                           ['02i1U000000OEbwQAG', '0011U000007zcnLQAQ', 'CTR 0012', '', '', 'RTR-MPA-0002-2002-0086',
                            'RTR-CTR-0001-2022-0012', '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000000OEc6QAG', '0011U000007zcnLQAQ', 'CTR 0013', '', '', 'RTR-MPA-0002-2002-0057',
                            'RTR-CTR-0001-2022-0013', '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000000OEcBQAW', '0011U000007zcnLQAQ', 'MPA 0073', '', '', '2 2.1 0073', '2 2.1 0073',
                            '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000000OEcQQAW', '0011U000007zcnLQAQ', 'MPA 0069', '', '', '2 2.1 0069',
                            '2 2.1 0069', '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000000OEcGQAW', '0011U000007zcnLQAQ', 'CTR 0014', '', '', 'RTR-MPA-0002-2002-0073',
                            'RTR-CTR-0001-2024-0014', '6/14/2021', 'Johnan Corp', ''],
                           ['02i1U000000HtulQAC', '0011U00000RZOa0QAH', 'MPA 0012', '', '', '2 2.1 0012', '2 2.1 0012',
                            '', 'Honda', '0011U000007zcnLQAQ'],
                           ['02i1U000003mDAPQA2', '0011U000007zcnLQAQ', 'CTR 0072', '', '', 'RTR-MPA-0003-2038-0233',
                            'RTR-CTR-0001-2043-0072', '', 'Johnan Corp', ''],
                           ['02i1U0000006IjXQAU', '0011U000008D4m1QAC', 'MPA 0034', '', '', '2 2.1 0034', '2 2.1 0034',
                            '', 'Nachi Technology Inc', '0011U000007zcnLQAQ'],
                           ['02i1U0000006IkBQAU', '0011U00001OFhARQA1', 'MPA 0042', '', '', '2 2.1 0042', '2 2.1 0042',
                            '', 'Kyoto University', '0011U000007zcnLQAQ'],
                           ['02i1U0000006IioQAE', '0011U000008D4m1QAC', 'MPA 0025', '', '', '2 2.1 0025', '2 2.1 0025',
                            '', 'Nachi Technology Inc', '0011U000007zcnLQAQ'],
                           ['02i1U0000006IitQAE', '0011U000007zcdGQAQ', 'MPA 0026', '', '', '2 2.1 0026', '2 2.1 0026',
                            '', 'Sony Electronics Inc', '0011U000007zcnLQAQ'],
                           ['02i1U0000006IjNQAU', '0011U000007zcnLQAQ', 'MPA 0032', '', '', '2 2.1 0032', '2 2.1 0032',
                            '', 'Johnan Corp', '']])

        self.assertEqual(expected, result)

    def test_get_all_assets_by_distributor_invalid(self):
        result = self.accounts.get_all_assets_by_distributor('0011U000008D4kPQAS')
        expected = []

        self.assertEqual(expected, result)

    def test_split_assets_by_distributor_johnan(self):
        account_split = AccountsAndAssets('distributors_and_children.csv', 'all_assets_from_distributors.csv')
        result = sorted(account_split.split_assets_by_distributor()['0011U000007zcnLQAQ'].tolist())
        johnan_assets_df = pd.read_csv('test/johnan-corp_assets_expected.csv')
        expected_johnan = file_prep(johnan_assets_df)
        # print('expected johnan: ', expected_johnan)
        # print('result: ', result)
        self.assertEqual(expected_johnan, result)

    def test_split_assets_by_distributor_nexty(self):
        account_split = AccountsAndAssets('distributors_and_children.csv', 'all_assets_from_distributors.csv')
        result = sorted(account_split.split_assets_by_distributor()['0011U000008Dh2dQAC'].tolist())
        nexty_assets_df = pd.read_csv('test/nexty_assets_expected.csv')
        expected_nexty = file_prep(nexty_assets_df)
        # print('expected nexty: ', expected_nexty)
        # print('result: ', result)
        self.assertEqual(expected_nexty, result)

    def test_all_distributors_split(self):
        account_split = AccountsAndAssets('distributors_and_child_accounts.csv', 'all_assets_from_distributors.csv')
        account_split.split_assets_and_save_csv()


class TestCombinedFiles(TestCase):
    def setUp(self) -> None:
        self.combined_files = CombinedFiles('distributors_and_children.csv', 'test/B.csv')


class TestInitAppendFiles(TestCombinedFiles):
    def __int__(self):
        self.maxDiff = None

    def test_empty_files_to_append(self):
        """
        Test when files are empty.
        Shouldn't raise an exception and should just print to screen a notification that no files or some were empty.
        :return: None
        """

    def test_some_empty_files(self):
        """
        Test when some files are empty and append is attempted.
        Should notify user of which files were empty.
        :return: None
        """

    def test_add_file_valid(self):
        """
        Test the add file method in the CombinedFiles class. No exception raise.
        :return: None
        """
        self.combined_files.add_file('test/real_data/real_data_A.csv')
        result = self.combined_files.get_files['test/real_data/real_data_A.csv']
        try:
            f_dataframe = pd.read_csv('test/real_data/real_data_A.csv')
        except IOError:
            raise Exception("Assets file not found.")

        f_header = f_dataframe.columns.tolist()
        f = f_dataframe.fillna('').to_numpy()
        expected = np.vstack((f_header, f)).tolist()

        self.assertEqual(result, expected)

    def test_combine_files(self):
        """
        Test the combine file method
        :return: None
        """
        self.combined_files.add_file('test/real_data/real_data_A.csv')
        self.combined_files.add_file('test/real_data/real_data_B.csv')
        self.combined_files.combine_files()
        result = self.combined_files.get_combined_list
        try:
            f_dataframe = pd.read_csv('test/real_data/real_data_combined.csv')
        except IOError:
            raise Exception("Assets file not found.")

        f_header = f_dataframe.columns.tolist()
        f = f_dataframe.fillna('').to_numpy()
        expected = np.vstack((f_header, f)).tolist()

        self.assertEqual(sorted(result), sorted(expected))

    def test_add_file_invalid(self):
        """
        Test the add file method in CombinedFiles class. Exception raise.
        :return: None
        """

    def test_custom_no_file_found_in_dir_exception(self):
        """
        Test when files are not placed in the proper directory.
        This should raise a custom exception (catching file read exception) and instruct user where to place files
        and what the file should be named (?).
        :return: None
        """

    def test_show_changes(self):
        """
        Test the change tracking.
        :return: None
        """
        self.combined_files.add_file('test/real_data_changed_A.csv')
        self.combined_files.combine_files()
        expected = []
        result = self.combined_files.show_changes()
        self.assertEqual(result, expected)

    def test_show_changes_real_data(self):
        """
        Test the change tracking with real data
        :return: None
        """
        combined_files_changes = CombinedFiles('distributors_and_children.csv', 'test/real_data/real_data_combined.csv')
        combined_files_changes.add_file('test/real_data/real_data_A_changed.csv')
        combined_files_changes.add_file('test/real_data/real_data_B_changed.csv')
        combined_files_changes.combine_files()
        result = combined_files_changes.show_changes()
        expected = [[['02i1U000003m9emQAA', '0011U000007zcnLQAQ', 'CTR 0042', '', '', '', 'RTR-MPA-0003-2031-0201', 'RTR-CTR-0001-2032-0042', '9/28/2021', 'Johnan Corp', ''],
                     ['02i1U000003m9emQAA', '0011U000008D4kPQAS', 'CTR 0042', '', '', '', 'RTR-MPA-0003-2031-0201', 'RTR-CTR-0001-2032-0042', '9/28/2021', 'Johnan Corp', '']],
                    [['02i1U000003mD1kQAE', '0011U00000pT9FAQA0', 'MPA 0225', '', '', '', 'RTR-MPA-0003-2038-0225', 'RTR-MPA-0003-2038-0225', '', 'Next.Robotics', ''],
                     ['02i1U000003mD1kQAE', '0011U000007zcnLQAQ', 'MPA 0225', '', '', '', 'RTR-MPA-0003-2038-0225', 'RTR-MPA-0003-2038-0225', '', 'Next.Robotics', '']]]
        self.assertEqual(result, expected)

    def test_show_changes_no_changes(self):
        """
        Test the change tracking with real data
        :return: None
        """
        combined_files_changes = CombinedFiles('distributors_and_children.csv', 'test/real_data/real_data_combined.csv')
        combined_files_changes.add_file('test/real_data/real_data_A.csv')
        combined_files_changes.add_file('test/real_data/real_data_B.csv')
        combined_files_changes.combine_files()
        result = combined_files_changes.show_changes()
        expected = []
        self.assertEqual(result, expected)

    def test_get_inventory_change_number(self):
        """
        Tests the get_inventory_change_number method that returns how many changes were made to the AccountId field
        :return: None
        """
        combined_files_changes = CombinedFiles('distributors_and_children.csv', 'test/real_data/real_data_combined.csv')
        combined_files_changes.add_file('test/real_data/real_data_A_changed.csv')
        combined_files_changes.add_file('test/real_data/real_data_B_changed.csv')
        combined_files_changes.combine_files()
        combined_files_changes.show_changes()
        result = combined_files_changes.get_inventory_change_number()
        expected = 2

        self.assertEqual(result, expected)

    def test_get_inventory_change_number_no_change(self):
        """
        Tests the get_inventory_change_number method that returns how many changes were made to the AccountId field
        :return: None
        """
        combined_files_changes = CombinedFiles('distributors_and_children.csv', 'test/real_data/real_data_combined.csv')
        combined_files_changes.add_file('test/real_data/real_data_A.csv')
        combined_files_changes.add_file('test/real_data/real_data_B.csv')
        combined_files_changes.combine_files()
        combined_files_changes.show_changes()
        result = combined_files_changes.get_inventory_change_number()
        expected = 0

        self.assertEqual(result, expected)

    def test_write_combined_file(self):
        """
        Tests the write_combined_file method.
        :return: None
        """
        combined_files_changes = CombinedFiles('distributors_and_children.csv', 'test/real_data/real_data_combined.csv')
        combined_files_changes.add_file('test/real_data/real_data_A.csv')
        combined_files_changes.add_file('test/real_data/real_data_B.csv')
        combined_files_changes.combine_files()
        combined_files_changes.show_changes()
        combined_files_changes.write_combined_file()

    '''
    def test_invalid_change(self):
        """
        Test when distributor makes bad change to file.
        :return: None
        """
    '''
