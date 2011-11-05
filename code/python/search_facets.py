#!/usr/bin/env python

import json
import logging
import sys
import xapian

def search(dbpath, querystring, offset=0, pagesize=10):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve

    # Open the database we're going to search.
    db = xapian.Database(dbpath)

    # Set up a QueryParser with a stemmer and suitable prefixes
    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("en"))
    queryparser.add_prefix("title", "S")
    queryparser.add_prefix("description", "XD")

    # And parse the query
    query = queryparser.parse_query(querystring)

    # Use an Enquire object on the database to run the query
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    # And print out something about each match
    matches = []
    
    # Set up a spy to inspect the MAKER value at slot 1
    spy = xapian.ValueCountMatchSpy(1)
    enquire.add_matchspy(spy)
        
    for index, match in enumerate(enquire.get_mset(offset, pagesize, 100)):
        fields = json.loads(match.document.get_data())
        print u"%(rank)i: #%(docid)3.3i %(title)s" % {
            'rank': offset + index + 1,
            'docid': match.docid,
            'title': fields.get('TITLE', u''),
            }
        matches.append(match.docid)

        # Parse and display the spy values 
    for facet in spy.values():
        print u"Facet: %(term)s; count: %(count)i" % {
            'term' : facet.term,
            'count' : facet.termfreq
        }
    
    # Finally, make sure we log the query and displayed results
    logger = logging.getLogger("xapian.search")
    logger.info(
        "'%s'[%i:%i] = %s",
        querystring,
        offset,
        offset + pagesize,
        ' '.join([str(docid) for docid in matches]),
        )

logging.basicConfig(level=logging.INFO)
search(dbpath = sys.argv[1], querystring = " ".join(sys.argv[2:]))