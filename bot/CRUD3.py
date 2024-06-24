def get_sentence(lang: str, user_id: int):
    if lang == 'ru':
        return '''
                select ru, sentence_id, corpus from corpus.parallel_corpus
                where ((ru is not null and bua is null) 
                    or (ru is not null and bua is not null and check_1 is False and check_2 is False))
                    and incorrect_flg is False
                order by random()
                limit 1
            '''
    elif lang == 'bua':
        return '''
                select bua, sentence_id, corpus from corpus.parallel_corpus
                where ((bua is not null and ru is null) 
                    or (bua is not null and ru is not null and check_1 is False and check_2 is False))
                    and incorrect_flg is False
                order by random()
                limit 1
            '''
    elif lang == 'both':
        return f'''
                select * from (
                    select 
                        bua, 
                        ru,
                        corpus,
                        sentence_id 
                    from corpus.parallel_corpus
                    where bua is not null 
                        and ru is not null
                        and ((check_1 is null or check_2 is null) or check_1 != check_2)
                        and (user_sentence != {user_id} or user_sentence is null)
                        and (user_check_1 != {user_id} or user_check_1 is null)
                        and (user_check_2 != {user_id} or user_check_2 is null)
                        and bua != 'некорректное предложение'
                        and ru != 'некорректное предложение'
                        and incorrect_flg is False
                )
                order by random()
                limit 1
            '''


def update_translation(sentence: str, sentence_id: int, user_id: int, lang: str, boolean: bool=True) -> str:
    if lang == 'ru':
        return f'''
                update corpus.parallel_corpus
                set bua = '{sentence}',
                    user_sentence = {user_id},
                    check_1 = null,
                    check_2 = null,
                    user_check_1 = null,
                    user_check_2 = null,
                    incorrect_flg = False,
                    processed_dttm = now()
                where sentence_id = {sentence_id} 
        '''
    elif lang == 'bua':
        return f'''
                    update corpus.parallel_corpus
                    set ru = '{sentence}',
                        user_sentence = {user_id},
                        check_1 = null,
                        check_2 = null,
                        user_check_1 = null,
                        user_check_2 = null,
                        incorrect_flg = False,
                        processed_dttm = now()
                    where sentence_id = {sentence_id} 
            '''
    elif lang == 'both':
        return f'''
                update corpus.parallel_corpus
                set check_1 = case when check_1 is null then {boolean}
                        when check_1 != check_2 and check_1 != {boolean} then {boolean} 
                        else check_1 end,
                    check_2 = case when check_1 is null then null 
                        when check_1 is not null and check_2 is null then {boolean} 
                        when check_1 != check_2 and check_2 != {boolean} then {boolean}
                        else check_2 end,
                    user_check_1 = case when check_1 is null then {user_id}
                        when check_1 != check_2 and check_1 != {boolean} then {user_id} 
                        else user_check_1 end,
                    user_check_2 = case when check_1 is null then null 
                        when check_1 is not null and check_2 is null then {user_id} 
                        when check_1 != check_2 and check_2 != {boolean} then {user_id}
                            else user_check_2 end,
                    incorrect_flg = False,
                    processed_dttm = now()
                where sentence_id = {sentence_id}
            '''


def insert_two_sentences(sentence_ru: str, sentence_bua: str, which_corpus: str, user_id: int) -> str:
    return f'''
        insert into corpus.parallel_corpus (bua, ru, corpus, user_sentence, processed_dttm)
            values (
                '{sentence_bua}',
                '{sentence_ru}',
                '{which_corpus}',
                {user_id},
                now()
            )
            '''


def mark_sentence_incorrect(sentence_id: int, user_id: int) -> str:
    return f'''
                update corpus.parallel_corpus
                set 
                    incorrect_flg = True, 
                    user_check_1 = {user_id},
                    processed_dttm = now()
                where sentence_id = {sentence_id}
            '''


# statistics

def get_count_all_sentences() -> str:
    return '''
        select sum(count) 
        from (
            select count(distinct sentence_id)
            from corpus.parallel_corpus
            where corpus = 'монокорпус бурятского' and ru is not null
            union all 
            select count(distinct sentence_id)
            from corpus.parallel_corpus
            where corpus = 'FLORES' and bua is not null
            ) t
    '''


def get_count_checked() -> str:
    return '''
        select count(*)
        from corpus.parallel_corpus
        where check_1 is not null
    '''


def get_count_bua_sentences() -> str:
    return '''
        select count(distinct sentence_id)
        from corpus.parallel_corpus
        where corpus = 'FLORES' and bua is not null
    '''


def get_count_ru_sentences() -> str:
    return '''
        select count(distinct sentence_id)
        from corpus.parallel_corpus
        where corpus = 'монокорпус бурятского' and ru is not null
    '''


def get_count_users() -> str:
    return '''
        select count(distinct user_id) 
        from (
            select user_sentence as user_id
            from corpus.parallel_corpus
            union all 
            select user_check_1 as user_id
            from corpus.parallel_corpus
            union all 
            select user_check_2 as user_id
            from corpus.parallel_corpus
            ) t
    '''