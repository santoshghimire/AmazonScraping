import functools


def check_spider_pipeline(process_item_method):

    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        # msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        try:
            if self.__class__ in spider.pipeline:
                # spider.log(msg % 'executing', level=log.DEBUG)
                return process_item_method(self, item, spider)

            # otherwise, just return the untouched item (skip this step in
            # the pipeline)
            else:
                # spider.log(msg % 'skipping', level=log.DEBUG)
                return item
        except:
            return item

    return wrapper


def check_spider_connection(spider_connection_method):

    @functools.wraps(spider_connection_method)
    def wrapper(self, spider):

        # message template for debugging
        # msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        try:
            if self.__class__ in spider.pipeline:
                # spider.log(msg % 'executing', level=log.DEBUG)
                return spider_connection_method(self, spider)

            # otherwise, just return the untouched item (skip this step in
            # the pipeline)
            else:
                # spider.log(msg % 'skipping', level=log.DEBUG)
                return
        except:
            return

    return wrapper
