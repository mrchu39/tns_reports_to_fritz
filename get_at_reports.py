import requests
import pandas as pd
import numpy as np
import json
import simplejson
import datetime

TNS_API_KEY = '54916f1700966b3bd325fc1189763d86512bda1d'
YOUR_BOT_ID = '48869'
YOUR_BOT_NAME = "ZTF_Bot1"
FRITZ_TOKEN = 'a5ffd9e6-8263-454b-9ec0-d36911df297d'

def hms2deg(num):
    return float(num.split(':')[0])*360./24 + float(num.split(':')[1])*360./(24*60) + float(num.split(':')[2])*360./(24*60*60)

def dms2deg(num):
    if num[0] == '-':
        return float(num.split(':')[0]) - float(num.split(':')[1])*360./(360*60) - float(num.split(':')[2])*360./(360*60*60)
    else:
        return float(num.split(':')[0]) + float(num.split(':')[1])*360./(360*60) + float(num.split(':')[2])*360./(360*60*60)

def get_at_reports(days_since=1):
    query_url = 'https://www.wis-tns.org/search?&discovered_period_value='+str(days_since)+'&discovered_period_units=days&unclassified_at=1&classified_sne=0&include_frb=0&name=&name_like=0&isTNS_AT=yes&public=all&ra=&decl=&radius=&coords_unit=arcsec&reporting_groupid%5B%5D=null&groupid%5B%5D=null&classifier_groupid%5B%5D=null&objtype%5B%5D=null&at_type%5B%5D=null&date_start%5Bdate%5D=&date_end%5Bdate%5D=&discovery_mag_min=&discovery_mag_max=19&internal_name=&discoverer=&classifier=&spectra_count=&redshift_min=&redshift_max=&hostname=&ext_catid=&ra_range_min=&ra_range_max=&decl_range_min=-30&decl_range_max=90&discovery_instrument%5B%5D=null&classification_instrument%5B%5D=null&associated_groups%5B%5D=null&official_discovery=0&official_classification=0&at_rep_remarks=&class_rep_remarks=&frb_repeat=all&frb_repeater_of_objid=&frb_measured_redshift=0&frb_dm_range_min=&frb_dm_range_max=&frb_rm_range_min=&frb_rm_range_max=&frb_snr_range_min=&frb_snr_range_max=&frb_flux_range_min=&frb_flux_range_max=&num_page=50&display%5Bredshift%5D=1&display%5Bhostname%5D=1&display%5Bhost_redshift%5D=1&display%5Bsource_group_name%5D=1&display%5Bclassifying_source_group_name%5D=1&display%5Bdiscovering_instrument_name%5D=0&display%5Bclassifing_instrument_name%5D=0&display%5Bprograms_name%5D=0&display%5Binternal_name%5D=1&display%5BisTNS_AT%5D=0&display%5Bpublic%5D=1&display%5Bend_pop_period%5D=0&display%5Bspectra_count%5D=1&display%5Bdiscoverymag%5D=1&display%5Bdiscmagfilter%5D=1&display%5Bdiscoverydate%5D=1&display%5Bdiscoverer%5D=1&display%5Bremarks%5D=0&display%5Bsources%5D=0&display%5Bbibcode%5D=0&display%5Bext_catalogs%5D=0'
    headers={'User-Agent':'tns_marker{"tns_id":'+str(YOUR_BOT_ID)+', "type":"bot", "name":"'+YOUR_BOT_NAME+'"}'}

    response = requests.get(query_url, headers=headers)

    body = response.text.split('Showing results')[1]
    body_list = body.split('</tbody>\n</table>\n</div></td> </tr>\n</tbody>\n</table>\n</div></td> </tr>')[:-1]

    obj_list = []
    int_name = []
    ras = []
    decs = []
    mags = []
    disc_date = []

    for b, body_it in enumerate(body_list):
        if b == 0:
            body_it = body_it.split('tbody', 1)[1]

        obj_list.append(body_it.split('cell-name')[1].split('</a>')[0].split('>')[-1])
        int_name.append(body_it.split('cell-internal_name">')[1].split('<')[0])
        ras.append(body_it.split('cell-ra">')[1].split('<')[0])
        decs.append(body_it.split('cell-decl">')[1].split('<')[0])
        mags.append(body_it.split('cell-flux">')[2].split('<')[0])
        disc_date.append(body_it.split('cell-discoverydate">')[1].split('<')[0])

    obj_df = pd.DataFrame(np.vstack((obj_list, int_name, ras, decs, mags, disc_date)).T, columns=['Objects', 'Internal Name', 'RA', 'Dec', 'Discovery Mag', 'Discovery Date'])

    return obj_df

def submit_tns_alerts(days_since=1):
    obj_df = get_at_reports(days_since)

    for o in range(len(obj_df)):

        headers = {'Authorization': f'token {FRITZ_TOKEN}'}
        data = {
            'ra': hms2deg(obj_df['RA'][o]),
            'dec': dms2deg(obj_df['Dec'][o]),
            'id': obj_df['Internal Name'][o],
            'filter_ids': [128],
            'passed_at': obj_df['Discovery Date'][o]
        }

        while True:
            try:
                response = requests.post('https://fritz.science/api/candidates', headers=headers, data=json.dumps(data))

                if json.loads(response.text)['status'] == 'error':
                    if 'duplicate key value violates unique constraint' in json.loads(response.text)['message']:
                        print(str(datetime.datetime.utcnow()) + ': ' + obj_df['Internal Name'][o] + ' has already been uploaded to Fritz.')

                        return

                    print(str(datetime.datetime.utcnow()) + ': Submission failed. Error: ' + json.loads(response.text)['message'])
		    
                    return

                print(str(datetime.datetime.utcnow()) + ': Submission of ' + obj_df['Internal Name'][o] + ' succeeded.')

                return

            except simplejson.decoder.JSONDecodeError:
                continue
