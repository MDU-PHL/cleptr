# for row in tab.iterrows():
#     isolate_dict[row[1]['ID']] = {
#         'cgmlst_scheme': 'salmonella_mdu_2021',
#         'current': '14/06/2021',
#         'data_available': 'historical',
#         '14/06/2021': {'CT':row[1]['Tx:50'], 'to_report':f"{row[1]['SEROTYPE']}:{row[1]['ST']}:{row[1]['Tx:50']}"},
#         'serotype': row[1]['SEROTYPE'],
#         'mlst':row[1]['ST']
#     }
# isolate_dict


import csv,json, logging, datetime, pathlib, pandas
from hashlib import new
from cleptr.CustomLog import CustomFormatter


LOGGER =logging.getLogger(__name__) 
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
fh = logging.FileHandler('cleptr.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p') 
fh.setFormatter(formatter)
LOGGER.addHandler(ch) 
LOGGER.addHandler(fh)

class Cleptr(object):

    def _check_file(self, path):

        if pathlib.Path(path).exists():
            LOGGER.info(f"The file {path} has been found")
            return True
        else:
            LOGGER.warning(f"Something has gone wrong. File : {path} does not exist. Please check your input and try again.")
            return False

    def _open_file(self, input_file, delimiter = ','):
        """
        open a csv or tsv and return a list of dicts with each dict representing a row
        """
        try:
            with open(input_file, 'r') as f:
                reader = csv.DictReader(f, delimiter = delimiter)
                data = [row for row in reader]
            return data

        except FileNotFoundError:
            LOGGER.critical(f"Something has gone wrong with reading the file: {input_file}. Exiting, please try again.")
            raise SystemExit
    
    def _open_json(self, input_file):
        """
        open a json file - return a dictionary
        """
        try:

            with open(input_file, 'r') as j:
                _dict = json.load(j)

                return _dict
        except FileNotFoundError:
            LOGGER.critical(f"Something has gone wrong with reading the file: {input_file}. Exiting, please try again.")

    def _save_json(self, _dict, outputname):
        """
        Save a dictionary as a json file
        """

        try:
            o = pathlib.Path(outputname).name
            with open(o, 'w') as j:
                json.dump(_dict, j)
        except PermissionError:
            LOGGER.critical(f"It seems something that you do not have permission to update this file : {outputname}. Sorry.")
            raise SystemExit
    
    def _generate_cluster_dict(self, _data):

        cluster_dict = {}
        for row in _data:
            # print(row)
            if f"{row[self.cluster_col]}" not in cluster_dict:
                cluster_dict[f"{row[self.cluster_col]}"] = [row[self.id_col]]
            else:
                cluster_dict[f"{row[self.cluster_col]}"].append(row[self.id_col])
        # print(cluster_dict['UC'])
        return cluster_dict


    def _generate_sample_dict(self, _data, analysis_date, database_name, id_col, cluster_col):
        
        sample_dict = {}
        for row in _data:
            sample_dict[row[id_col]] = {
                'cgmlst_scheme': database_name,
                'date_added': analysis_date,
                'date_updated': analysis_date,
                'current': analysis_date,
                'clusters': {
                    analysis_date: f"{row[cluster_col]}"
                    }
            }
        return sample_dict
    
    def _get_date_analysed(self):
        """
        get the current date for use in database
        """
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _check_inputs(self, _inputs):

        for f in _inputs:
            if not self._check_file(path = f):
                return False
        return True

    def _guess_delimiter(self, input_file):

        if input_file.endswith('csv'):
            return ','
        else:
            with open(input_file, 'r') as f:
                header = f.readlines()[0]
                if len(header.strip().split('\t')) >1:
                    return '\t'
                else:
                    LOGGER.critical(f"Delimiter of file could not be detected. Please check your input files and try again.")
                    raise SystemExit

    def _get_header(self, input_file):

        
        with open(input_file, 'r') as f:
            h = f.readlines()[0]
            header = h.strip().split(delimiter)
            return header

    def _check_prefix(self, prefix):

        if prefix == '':
            LOGGER.critical(f"Prefix can not be empty. Please try again")
            raise SystemExit
        else:
            return True

class InitCleptr(Cleptr):

    def __init__(self,args):

        self.input = args.input
        self.cluster_col = args.cluster_col
        self.id_col = args.id_col
        self.database_name = args.database_name
        self.prefix = args.prefix
    
    def init_db(self):

        analysis_date = self._get_date_analysed()
        LOGGER.info(f"Analysis date is : {analysis_date}")
        if self._check_file(path = self.input):
            LOGGER.info(F"Now getting started on wrangling!")
            _data = self._open_file(input_file=self.input, delimiter= '\t')
            LOGGER.info(f"Initialising dictionaries for cleptr")
            cluster_dict = self._generate_cluster_dict(_data = _data)
            sample_dict = self._generate_sample_dict(_data = _data, analysis_date = analysis_date, id_col=self.id_col, cluster_col=self.cluster_col, database_name=self.database_name)
            LOGGER.info(f"Saving the sample db : {self.prefix}_samples.json")
            self._save_json(_dict = sample_dict, outputname=f"{self.prefix}_samples.json")
            LOGGER.info(f"Saving the cluster db : {self.prefix}_clusters.json")
            self._save_json(_dict = cluster_dict, outputname=f"{self.prefix}_clusters.json")

            LOGGER.info(f"Files for {self.prefix} have been initialised. You can now run cleptr report to generate output and cleptr run on any new analysis.")
        else:
            LOGGER.critical(f"There is something wrong with your input files, cleptr init can not proceed. Please try again.")
            raise SystemExit

class RunCleptr(Cleptr):

    def __init__(self, args):
        
        self.input = args.input
        self.clusters_db = args.clusters_db
        self.sample_db = args.sample_db
        self.cluster_col = args.cluster_col
        self.id_col = args.id_col
        self.database_name = args.database_name
        # self.prefix = args.

    def _check_no_change(self,orig, new):
        """
        There has been no change to the cluster
        """
        
        if orig == new:
            return True
        else:
            return False

    def _check_simple_merge(self,orig, new):
        """
        where the new cluster contains ALL of the samples from the original cluster
        """
    #     if orig != new:
        if orig != new and orig.union(new) == new:
            return True
        else:
            return False
        
    def _check_complex_case(self,orig, new):
        """
        where some part of a cluster is shared between old and new
        """
        
        if orig.intersection(new) != set() and orig != new:
            return True
        else:
            return False

    def _name_clusters(self,clusters_taken, results,current_id, new_results, prev = []):
        """
        rename clusters
        """
    #     print(current_dict)
    #     print(current_id)

        # print(f"Previous:{len(prev)}")
        # print(f"Previous:{prev}")
        if current_id != 'UC':
            new_id = max(clusters_taken) + 1
            clusters_taken.append(new_id)
        else:
            LOGGER.info(f"UC samples have been found")
            new_id = 'UC'
        
    #     to_report = f"{new_id}{suff}"
        results[f"{new_id}"] = {}
        results[f"{new_id}"] = new_results[current_id]
    #     results[f"{new_id}"]['serotype'] = list(current_dict[current_id]['serotype'])
    #     results[f"{new_id}"]['mlst'] = list(current_dict[current_id]['mlst'])
        
        
        
        return clusters_taken, results
#         print(new)
    def _make_clusters(self, prev_results, new_results):
        results = {} # a dictionary to store resutls in
        clusters_taken = sorted([int(i) for i in list(prev_results.keys()) if i != 'UC']) # A list of names taken - can not be re-used
        # print(clusters_taken)
        # print(new_results)
        # print(prev_results)
        for new in new_results: # for each cluster in recent dataset
            # print(new)
            cs = set()
            if new != 'UC':
                # print(new)
                # if new == '636':
                new_samples = set(sorted(new_results[new]))
                # print(new_samples)
                c = 0 # this is a counter to test how many original clusters a new cluster is comprised of
                # a list to track the clusters which overlap
        #     tracks which cluster type is triggered
                not_changed = False
                simple_merge = False
                splits = False
                uc = False
#             print(new_samples)
                for orig in prev_results:
                    # print(orig)
                    orig_samples = set(sorted(prev_results[orig]))
                    # print(orig_samples)
                    if self._check_no_change(orig = orig_samples, new = new_samples):
                        # print(orig_samples)
                        results[orig] = prev_results[orig]
                        # results[orig]['updated'] = False
                        not_changed = True
                        cs.add(orig)
                    elif self._check_complex_case(orig = orig_samples, new = new_samples):
                        if self._check_simple_merge(orig = orig_samples, new = new_samples):
                            simple_merge = True
                        else:
                            splits = True
                        c +=1
                        cs.add(orig)
            
                    # break
                # uc = True
            
                cs_no_uc = list(set([i for i in cs if i != 'UC']))
                # print(cs_no_uc)
                # print(simple_merge)
                if not_changed: # simple case 2 a cluster contains samples from a single orig cluster and new samples
                    # LOGGER.info(f'Not changed : {new_samples} were cluster in previous results')
                    pass
        #             print(list(cs)[0])
                elif simple_merge  and len(cs_no_uc) == 1: # simple case where a new cluster contains all samples from a previous clusters - ie a merging event previous names will not be used again since they are no longer clusters
                    # LOGGER.info(f"A simple merging event has occured - only new or unclustered samples added to existing cluster {cs_no_uc[0]}.")
                    results[list(cs_no_uc)[0]]= list(new_samples)
                elif simple_merge  and len(cs_no_uc) > 1:
                    # LOGGER.info(f"A simple merge event has occured - {';'.join(cs_no_uc)} clusters have merged.")
                    clusters_taken, results = self._name_clusters(clusters_taken = clusters_taken, results = results
                                                            ,current_id=new, new_results = new_results, prev = list(cs_no_uc))
                elif splits:
                    # LOGGER.info(f"A split with or without a subsequent merge has occured.")
                    # LOGGER.info(f"These previous cluster desginations will be retired {';'.join(cs_no_uc)}")
                    clusters_taken, results = self._name_clusters(clusters_taken = clusters_taken, results = results
                                                            ,current_id=new, new_results = new_results, prev = list(cs_no_uc))
                elif uc:
                    # LOGGER.info(f"{len(new_results[new])} unclustered samples have been found")
                    raise SystemExit
                else:
                    LOGGER.info(f"A new cluster containing only new sequences has formed.")
                    clusters_taken, results = self._name_clusters(clusters_taken = clusters_taken, results = results
                                                            ,current_id=new, new_results = new_results)
                
            else:
                LOGGER.info(f"Found {len(new_results[new])} unclustered sequences.")
                results['UC'] = new_results[new]
                # break
        # for r in results:
        #     print(r)
        # print(results)
        return results

    

    def _update_sample(self, new_cluster_dict, sample_dict, analysis_date, database_name):
        
        for cluster in new_cluster_dict:
            isos = new_cluster_dict[cluster]
            for i in isos:
                if i in sample_dict:
                    current_date = sample_dict[i]['current']
                    if sample_dict[i]['clusters'][current_date] != cluster:
                        sample_dict[i]['current'] = analysis_date
                        sample_dict[i]['date_updated'] = analysis_date
                        sample_dict[i]['clusters'][analysis_date] = cluster
                else:
                    sample_dict[i] = {
                        'current': analysis_date,
                        'date_added': analysis_date,
                        'date_updated': analysis_date,
                        'clusters':{
                            analysis_date: cluster
                        },
                        "cgmlst_scheme":database_name
                    }

        return sample_dict

    def update_db(self):

        if self._check_inputs(_inputs = [self.input, self.clusters_db,  self.sample_db]):
            LOGGER.info(f"All input files are correct. cleptr will continue.")
            LOGGER.info(f"Extracting new data.")
            new_data = self._open_file(input_file=self.input, delimiter='\t')
            new_clusters = self._generate_cluster_dict(_data = new_data)
            cluster_dict = self._open_json(input_file=self.clusters_db)
            LOGGER.info(f"Will now try to maintain your nomenclature.")
            new_cluster_dict = self._make_clusters(prev_results=cluster_dict, new_results=new_clusters)
            # print(new_cluster_dict['UC'])
            LOGGER.info(f"Updating sample db")
            sample_dict = self._open_json(input_file=self.sample_db)
            new_sample_dict = self._update_sample(new_cluster_dict = new_cluster_dict, sample_dict = sample_dict, 
                                                    analysis_date = self._get_date_analysed(), database_name = self.database_name)
    
            # print(new_cluster_dict['366'])
            # print(new_sample_dict['2022-008990'])
            LOGGER.info(f"Saving the sample db : {self.sample_db}")
            self._save_json(_dict = new_sample_dict, outputname=f"{self.sample_db}")
            LOGGER.info(f"Saving the cluster db : {self.clusters_db}")
            self._save_json(_dict = new_cluster_dict, outputname=f"{self.clusters_db}")
        else:
            LOGGER.critical(f"There is something wrong with your input files, cleptr run can not proceed. Please try again.")
            raise SystemExit


class ReportCleptr(Cleptr):

    def __init__(self,args):
        
        self.sample_db = args.sample_db
        self.metadata = args.metadata
        self.id_col = args.id_col
        self.prefix = args.prefix
        
    
    def _get_prev(self, cluster_dict):
        
        sorted_dates = sorted(cluster_dict, reverse=True)
        if len(sorted_dates) < 2:
            return ''
        else:
            return sorted_dates[1]

    def _get_data(self, sample_dict, output_dict, iso):
        
        print(sample_dict[iso])
        crnt = sample_dict[iso]['current']
        clst = f"{sample_dict[iso]['clusters'][crnt]}"
        dte = sample_dict[iso]['date_added']
        db = sample_dict[iso]['cgmlst_scheme']
        updtd = sample_dict[iso]['date_updated']
        prev_date = self._get_prev(cluster_dict = sample_dict[iso]['clusters'])
        prev = f"{sample_dict[iso]['clusters'][prev_date]}" if prev_date != '' else prev_date
        output_dict['cgT'] = clst
        output_dict['previous_cgT'] = prev
        output_dict['date_added'] = dte
        output_dict['date_updated'] = updtd
        output_dict['cgmlst_scheme'] = db

        return output_dict


    def _make_report(self, sample_dict, metadata, id_col ):

        # generate a table
        LOGGER.info(f"Updating table for reporting.")
        if metadata !=[]:
            LOGGER.info(f"Combining metadata and cgMLST types.")
            for meta in metadata:
                iso = meta[id_col]

                meta = self._get_data(sample_dict = sample_dict, output_dict= meta, iso = iso)
            
            results = pandas.DataFrame(metadata,index = range(len(metadata)))
        else:
            LOGGER.info(f"Extracting data from samples json")
            data_list = []
            for sample in sample_dict:
                output_dict = {id_col: sample}
                output_dict = self._get_data(sample_dict = sample_dict, output_dict = output_dict, iso = sample)
                data_list.append(output_dict)
            results = pandas.DataFrame(data_list,index = range(len(data_list)))
        results = results.set_index(id_col)

        return results


   
    def report(self):

        if self._check_file(path = self.sample_db) and self._check_prefix(self.prefix):
            LOGGER.info(f"Your sample database is present. Checking for metadata.")
            if self.metadata != '' and self._check_file(path = self.metadata):
                LOGGER.info(f"You have supplied a valid path to a metadata file")
                LOGGER.info(f"Opening: {self.metadata}")
                # header_line = self._get_header(input_file = self.metadata)
                delimiter = self._guess_delimiter(input_file = self.metadata)
                metadata = self._open_file(input_file=self.metadata, delimiter=delimiter) # this is a list of dictionaries with data from metadata
            elif self.metadata != '' and not self._check_file(path = self.metadata):
                LOGGER.critical(f"You have supplied a path to metadata : {self.metadata} that is not a valid file path, cleptr report can not proceed.")
                raise SystemExit
            elif self.metadata == '':
                LOGGER.info(f'No metadata supplied.')
                metadata = []

            sample_dict = self._open_json(input_file=self.sample_db)

            report_tab = self._make_report(sample_dict = sample_dict, metadata = metadata, id_col = self.id_col)
            LOGGER.info(f"Saving report : {self.prefix}_report.csv")
            report_tab.to_csv(f"{self.prefix}_report.csv")


            






            # 'M2021-00354,2021-006426', 'M2021-00354,2021-006427', 'M2021-00354,2021-006428', 'M2021-00354,2021-006429', 'M2021-00354,2021-006430', 'M2021-00354,2021-006431', 'M2021-00354,2021-006432', 'M2021-00354,2021-006433', 'M2021-00354,2021-006434'