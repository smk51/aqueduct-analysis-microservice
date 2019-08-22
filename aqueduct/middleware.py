"""MIDDLEWARE"""
import logging
from functools import wraps

from flask import request

from aqueduct.errors import GeostoreNotFound
from aqueduct.routes.api import error
from aqueduct.services.geostore_service import GeostoreService


def remove_keys(keys, dictionary):
    for key in keys:
        try:
            del dictionary[key]
        except KeyError:
            pass
    return dictionary


def sanitize_parameters(func):
    """Sets any queryparams in the kwargs"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(f'[middleware] [sanitizer] args: {args}')
            myargs = dict(request.args)
            # Exclude params like loggedUser here
            sanitized_args = remove_keys(['loggedUser'], myargs)
            kwargs['params'] = sanitized_args
        except GeostoreNotFound:
            return error(status=404, detail='body params not found')

        return func(*args, **kwargs)

    return wrapper


def get_geo_by_hash(func):
    """Get geodata"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs["geostore"]:
            geostore = kwargs["geostore"]
            logging.info('[middleware]: Getting geostore with ID ' + geostore)
            if not geostore:
                return error(status=400, detail='Geostore is required')
            try:
                geojson = GeostoreService.get(geostore)

            except GeostoreNotFound:
                return error(status=404, detail='Geostore not found')
            kwargs["geojson"] = geojson
        return func(*args, **kwargs)

    return wrapper


def get_wra_params(func):
    """Get weight schema (wscheme) where applicable or return None"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            kwargs["geostore"] = request.args.get('geostore', None)
            wscheme = request.args.get('wscheme', None)
            kwargs["wscheme"] = wscheme
            analysis_type = request.args.get('analysis_type', None)
            kwargs["analysis_type"] = str(analysis_type)
            month = request.args.get('month', None)
            kwargs["month"] = str(month)
            year = request.args.get('year', None)
            kwargs["year"] = str(year)
            change_type = request.args.get('change_type', None)
            kwargs["change_type"] = str(change_type)
            indicator = request.args.get('indicator', None)
            kwargs["indicator"] = str(indicator)
            scenario = request.args.get('scenario', None)
            kwargs["scenario"] = str(scenario)
            locations = request.args.get('locations', None)
            kwargs["locations"] = locations
            input_address = request.args.get('input_address', None)
            kwargs["input_address"] = input_address
            match_address = request.args.get('match_address', None)
            kwargs["match_address"] = match_address
        elif request.method == 'POST':
            kwargs["geostore"] = request.json.get('geostore', None)
            wscheme = request.json.get('wscheme', None)
            kwargs["wscheme"] = wscheme
            analysis_type = request.json.get('analysis_type', None)
            kwargs["analysis_type"] = str(analysis_type)
            month = request.json.get('month', None)
            kwargs["month"] = str(month)
            year = request.json.get('year', None)
            kwargs["year"] = str(year)
            change_type = request.json.get('change_type', None)
            kwargs["change_type"] = str(change_type)
            indicator = request.json.get('indicator', None)
            kwargs["indicator"] = str(indicator)
            scenario = request.json.get('scenario', None)
            kwargs["scenario"] = str(scenario)
            locations = request.json.get('locations', None)
            kwargs["locations"] = locations
            input_address = request.json.get('input_address', None)
            kwargs["input_address"] = input_address
            match_address = request.json.get('match_address', None)
            kwargs["match_address"] = match_address

        logging.debug(f'[MIDDLEWARE - ws scheme]: {kwargs}')
        return func(*args, **kwargs)

    return wrapper
