# streamlit_dashboard_final_v2.py

import streamlit as st
import pandas as pd
from PIL import Image
import os
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
from streamlit_folium import st_folium
import folium
from matplotlib import cm, colors as mcolors



path = r"C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\data"
file_demand = "data_optimization_demand.xlsx"
file_candidate = "data_optimization_candidate.xlsx"
file_distance = "data_optimization_distance.xlsx"
file_school = "학교통합정보_cleaned.csv"

df_demand = pd.read_excel(os.path.join(path, file_demand))
df_candidate = pd.read_excel(os.path.join(path, file_candidate))
df_distance = pd.read_excel(os.path.join(path, file_distance))
df_school = pd.read_csv(os.path.join(path, file_school))

map_img = Image.open(r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\gyeonggi_cluster_map.png')

# 클러스터별 지역 리스트
cluster_regions = {
    0: [
        '경기도 파주시', '경기도 김포시', '경기도 남양주시', '경기도 이천시',
        '경기도 용인시 수지구', '경기도 용인시 처인구', '경기도 군포시', '경기도 하남시',
        '경기도 오산시', '경기도 평택시', '경기도 화성시', '경기도 수원시 권선구',
        '경기도 광주시', '경기도 안양시 만안구', '경기도 용인시 기흥구'
    ],
    1: [
        '경기도 여주시', '경기도 동두천시', '경기도 양평군'
    ],
    2: [
        '경기도 연천군', '경기도 가평군'
    ],
    3: [
        '경기도 안양시 동안구', '경기도 성남시 수정구', '경기도 광명시', '경기도 성남시 분당구',
        '경기도 수원시 영통구', '경기도 과천시', '경기도 부천시 원미구', '경기도 수원시 장안구',
        '경기도 고양시 일산동구', '경기도 고양시 덕양구', '경기도 고양시 일산서구',
        '경기도 구리시', '경기도 의왕시'
    ],
    4: [
        '경기도 수원시 팔달구', '경기도 안산시 상록구', '경기도 포천시',
        '경기도 안산시 단원구', '경기도 부천시 오정구', '경기도 의정부시',
        '경기도 시흥시', '경기도 부천시 소사구', '경기도 안성시',
        '경기도 양주시', '경기도 성남시 중원구'
    ]
}


# SHAP 이미지 파일명 매핑
cluster_shap_images = {
    0: r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\shap_summary_cluster_0.png',
    1: r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\shap_summary_cluster_1.png',
    2: r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\shap_summary_cluster_2.png',
    3: r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\shap_summary_cluster_3.png',
    4: r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\shap_summary_cluster_4.png',
}

# 클러스터별 변수 중요도 DataFrame
shap_importance_df = pd.read_csv(r'C:\Users\전지현\Documents\카카오톡 받은 파일\MOE\MOE\streamlit\SHAP_total.csv')  # Feature, 클러스터_0, 클러스터_1 ...
#--------------------------------------------------------------------------------------------#
# 페이지 설정
st.set_page_config(page_title="경기도 사교육 분석 대시보드", layout="wide")

# 탭 만들기
tab1, tab2 = st.tabs(["🏫 경기도 사교육 분석 대시보드", "🗺️ 지역별 학습자원 최적화"])
    
# 첫 번째 탭 (대시보드)
with tab1:
    st.title("🏫 경기도 사교육 분석 대시보드")
    # st.divider()  # 맨 위 구분선
    st.info("경기도 교육특성과 도시별 영향 요인을 분석합니다.")
    # --- 전체를 좌우로 나누기 ---
    left_col, col_mid, right_col = st.columns([4.9,0.2,4.9])  # 비율 조정

    # --- 왼쪽 : 지도 + 클러스터 지역 ---
    with left_col:
        st.subheader("🗺️ 경기도 시군구별 교육 특성 클러스터링")

        map_area, region_area = st.columns([6, 4])  # 지도:지역목록 내부 비율

        with map_area:
            st.image(map_img,  use_container_width=True)
    cluster_names = {
        0: ("사교육 중심 저투자형 지역", "#FAD7A0"),       # 살구색
        1: ("인프라 개선형 지역", "#D2B48C"),       # 연한 갈색
        2: ("인프라 개선형 지역", "#D5D8DC"),       # 회색
        3: ("사교육 중심 고투자형 지역", "#F5B7B1"), # 연한 빨강
        4: ("공교육 중심 저투자형 지역", "#A9DFBF"), # 연한 초록
    }

    with region_area:
        st.subheader("📋 클러스터별 지역 목록")
        for cluster_id, regions in cluster_regions.items():
            cluster_label, color = cluster_names.get(cluster_id, (f"클러스터 {cluster_id}", "#CCCCCC"))
            color_box = f'<span style="display:inline-block; width:12px; height:12px; background-color:{color}; margin-right:8px; border-radius:3px;"></span>'
            st.markdown(f"{color_box} **{cluster_label}**", unsafe_allow_html=True)
            st.markdown(", ".join(regions))
    with col_mid:
        # 세로 구분선
        st.markdown("<div style='height:1500px; border-left:1px solid lightgray;'></div>", unsafe_allow_html=True)

    # --- 오른쪽 : 지역별 SHAP 분석 ---
    with right_col:
        st.subheader("🔍 특정 지역별 SHAP 요약 분석")

        region_input = st.text_input("지역명을 입력하세요 (예: 경기도 성남시 분당구)")

        if region_input:
            # 클러스터 찾기
            cluster_found = None
            for cluster_id, regions in cluster_regions.items():
                for region in regions:
                    if region in region_input:
                        cluster_found = cluster_id
                        break
                if cluster_found is not None:
                    break

            if cluster_found is not None:
                st.success(f"📍 {region_input} 지역은 클러스터 {cluster_found} 에 속해 있습니다.")
                st.subheader("🗺️ 경기도 시군구별 교육 특성 클러스터링")

                shap_img_col, feature_table_col = st.columns([5, 5])  # shap:변수 테이블 비율

                with shap_img_col:
                    shap_img = Image.open(cluster_shap_images[cluster_found])
                    st.image(shap_img, use_container_width=True)

                with feature_table_col:
                    cluster_importance = shap_importance_df[['Feature', f'클러스터_{cluster_found}']].copy()
                    cluster_importance.columns = ['Feature', 'SHAP 평균값']
                    cluster_importance = cluster_importance.sort_values(by='SHAP 평균값', ascending=False)
                    st.dataframe(cluster_importance, height=500,hide_index=True)

            else:
                st.warning("❗ 해당 지역명을 클러스터에서 찾을 수 없습니다. 다시 입력해주세요.")


# 두 번째 탭 (학습자원 최적화)
with tab2:
    st.title("🗺️ 지역별 학습자원 최적화")
    st.info("지역별 맞춤 알고리즘을 통해 학습 자원을 최적화합니다.")

    def capacitated_MCLP(region, coverage_threshold, supply):
        # 같은 지역 내에서만 최적화
        df_demand_region = df_demand[df_demand['지역'] == region].copy()
        df_candidate_region = df_candidate[df_candidate['지역'] == region].copy()
        df_distance_region = df_distance[df_distance['지역'] == region].copy()

        # 수요 가중치 (공급 예정 수/전체 학생 수)
        total_students = df_demand_region["학생수"].sum()
        weight = supply / total_students

        # 수요지별 수요량
        demand_dict = {}
        for idx, row in df_demand_region.iterrows():
            key = (row['지역'], row['학교명'])
            demand_dict[key] = round(row['학생수'] * weight, 0)

        # 후보지의 용량
        capacity_dict = {}
        for idx, row in df_candidate_region.iterrows():
            key = (row['지역'], row['시설명'])
            capacity_dict[key] = row['예상좌석수']

        # 수요지와 후보지 간 도보거리
        distance_dict = {}
        for idx, row in df_distance_region.iterrows():
            key_demand = (row['지역'], row['학교명'])
            key_candidate = (row['지역'], row['시설명'])
            distance_dict[(key_demand, key_candidate)] = row['도보거리']

        # 동률 상황에서 후보지 우선순위용 가중치 정보
        candidate_weight = {}
        for idx, row in df_candidate_region.iterrows():
            key = (row['지역'], row['시설명'])
            candidate_weight[key] = row['좌석(인구)수*가중치']

        # 최종 선정된 시설과 각 시설에 할당된 수요지 및 할당량
        selected_facility = []  
        assignment = {}      

        # 할당된 수요량의 총합
        total_assigned_demand = 0 

        # 선정 가능한 후보지 도출
        for iteration in range(50):
            # 후보지에 할당된 수요량의 총합 > 용량인 경우, 중단
            if total_assigned_demand > supply:
                break

            # 모든 수요지의 수요량이 충족된 경우, 중단
            available_demand = {school: demand for school, demand in demand_dict.items() if demand > 0}
            if not available_demand:
                break

            # 후보지별 할당 가능한 수요와 커버리지 내 총 수요량
            candidate_values = {}  
            candidate_assignment = {}
            
            for candidate, capacity in capacity_dict.items():
                # 아직 선정되지 않은 후보지에 대하여
                if candidate in [fac for (_, fac) in selected_facility]:
                    continue

                # 해당 후보지의 커버리지 내 수요지
                eligible_schools = []
                for school, demand in available_demand.items():
                    if (school, candidate) in distance_dict and distance_dict[(school, candidate)] <= coverage_threshold:
                        eligible_schools.append((distance_dict[(school, candidate)], school))
                if not eligible_schools:
                    continue
                
                # 수요지들을 가까운 순으로 정렬
                eligible_schools.sort(key=lambda x: x[0])

                # 커버리지 내 총 수요량 < 용량의 0.8배 이하인 경우, 다음 후보지로
                total_possible_demand = sum(available_demand[school] for _, school in eligible_schools)
                if total_possible_demand < capacity*0.8:
                    break
                
                # 각 후보지에 수요지 및 수요량 할당
                remaining_capacity = capacity
                assigned_demand = 0
                assignment_list = [] 

                for _, school in eligible_schools:
                    if remaining_capacity <= 0:
                        break
                    school_demand = available_demand[school]
                    allocation = min(school_demand, remaining_capacity, supply - total_assigned_demand)
                    if allocation <= 0:
                        break
                    assignment_list.append((school, allocation))
                    remaining_capacity -= allocation
                    assigned_demand += allocation

                candidate_values[candidate] = (assigned_demand, total_possible_demand)
                candidate_assignment[candidate] = assignment_list

            # 할당 가능한 후보지가 없으면 종료
            if not candidate_values:
                break

            # 시설 선택 기준

            # (1) 할당된 수요량이 가장 큰 후보지
            max_assigned_demand = max(val[0] for val in candidate_values.values())
            best_candidates = [candidate for candidate, (ad, _) in candidate_values.items() if ad == max_assigned_demand]

            # (2) 후보지가 여러 개인 경우, 커버리지 내 총 수요가 가장 큰 후보지
            if len(best_candidates) > 1:
                max_total_possible = max(candidate_values[candidate][1] for candidate in best_candidates)
                best_candidates = [candidate for candidate in best_candidates if candidate_values[candidate][1] == max_total_possible]

            # (3) 후보지가 여러 개인 경우, 시설명이 "학교"로 끝나지 않는 후보지
            if len(best_candidates) > 1:
                non_school_candidates = [candidate for candidate in best_candidates if not candidate[1].endswith("학교")]
                if non_school_candidates:
                    best_candidates = non_school_candidates

            # (4) 후보지가 여러 개인 경우, "좌석(인구)수*가중치" 값이 가장 높은 후보지
            if len(best_candidates) > 1:
                best_candidates.sort(key=lambda c: candidate_weight.get(c, 0), reverse=True)
                best_candidates = [best_candidates[0]]

            # (5) 후보지가 여러 개인 경우, 해당 시설과 이름이 같은 수요지의 수요량이 가장 큰 후보지
            if len(best_candidates) > 1:
                max_same_name_demand = -1
                selected = []
                for candidate in best_candidates:
                    region_name, facility_name = candidate
                    same_name_demand = demand_dict.get((region_name, facility_name), 0)
                    if same_name_demand > max_same_name_demand:
                        max_same_name_demand = same_name_demand
                        selected = [candidate]
                    elif same_name_demand == max_same_name_demand:
                        selected.append(candidate)
                best_candidates = selected

            for candidate in best_candidates:
                selected_facility.append((iteration+1, candidate))
                assignment[candidate] = candidate_assignment[candidate]
                print(f"Iteration {iteration+1}: 시설 = {candidate}, 학교 = {candidate_assignment[candidate]}")
                
                for school, assigned_amt in candidate_assignment[candidate]:
                    demand_dict[school] = max(0, demand_dict[school] - assigned_amt)
                    total_assigned_demand += assigned_amt

            iteration += 1

        # 아직 미할당된 수요가 있는 학교 목록 출력
        not_covered_schools = [school for school, demand in demand_dict.items() if demand > 0]
        print("충족하지 못한 학교:", not_covered_schools)

        return selected_facility, assignment, not_covered_schools, total_assigned_demand
    def map_MCLP(region, selected_facility, assignment):
    # 1) 지역 필터링

        df_fac = df_candidate[df_candidate['지역'] == region].copy()
        df_sch = df_demand[df_demand['지역'] == region].copy()

        # 2) 지도 초기화 (기본 타일 끄기)
        center_lat = df_fac['위도'].mean()
        center_lon = df_fac['경도'].mean()
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles=None,           # 기본 OSM 비활성화
            control_scale=True
        )

        # 3) OSM 타일레이어 재추가 + 불투명도 설정
        folium.TileLayer(
            'OpenStreetMap',
            name='OSM (faded)',
            opacity=0.8,  # 0.0(완전투명) ~ 1.0(불투명)
            control=False
        ).add_to(m)

        # 4) iteration별 색상 통일 (tab10 10색)
        base10 = cm.get_cmap('tab10').colors
        hex10  = [mcolors.to_hex(c) for c in base10]
        iteration_list = sorted({iter_num for iter_num, _ in selected_facility})
        iter_to_color = {
            iter_num: hex10[i % len(hex10)]
            for i, iter_num in enumerate(iteration_list)
        }

        # 5) 시설 + 할당 학교 시각화
        for iter_num, (region_name, fac_name) in selected_facility:
            fac_row = df_fac[df_fac['시설명'] == fac_name]
            if fac_row.empty:
                continue
            fac_lat = fac_row.iloc[0]['위도']
            fac_lon = fac_row.iloc[0]['경도']
            color   = iter_to_color[iter_num]

            # (1) DivIcon: 색 배경 + iteration 숫자
            html = f"""
            <div style="
                background-color: {color};
                color: white;
                border-radius: 50%;
                text-align: center;
                font-size: 10pt;
                font-weight: bold;
                width: 24px;
                height: 24px;
                line-height: 24px;
                box-shadow: 0 0 3px #555;">
                {iter_num}
            </div>"""
            folium.Marker(
                location=(fac_lat, fac_lon),
                icon=folium.DivIcon(html=html),
                popup=f"{fac_name} (Iter {iter_num})",
                tooltip=f"{fac_name} (Iter {iter_num})"
            ).add_to(m)

            # (2) 할당된 학교 + 선 연결
            key = (region_name, fac_name)
            if key in assignment:
                for (school_region, sch_name), _ in assignment[key]:
                    sch_row = df_sch[df_sch['학교명'] == sch_name]
                    if sch_row.empty:
                        continue
                    sch_lat = sch_row.iloc[0]['위도']
                    sch_lon = sch_row.iloc[0]['경도']

                    folium.CircleMarker(
                        location=(sch_lat, sch_lon),
                        radius=5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        popup=sch_name,
                        tooltip=sch_name
                    ).add_to(m)

                    folium.PolyLine(
                        locations=[(fac_lat, fac_lon), (sch_lat, sch_lon)],
                        color=color,
                        weight=2,
                        opacity=0.7
                    ).add_to(m)

        return m

    if "optimized" not in st.session_state:
        st.session_state.optimized = False

    # 두 개의 열로 분할 (왼쪽: 설정 및 결과, 오른쪽: 지도)
    col1, col_mid, col2 = st.columns([5,1,4 ])  # 비율 조절 가능

    with col1:    
        region_input = st.selectbox("지역 선택", df_demand['지역'].unique())
        supply_input = st.slider("공급 가능한 총 좌석 수", min_value=100, max_value=10000, step=100, value=300)
        coverage_threshold = st.slider("커버리지 거리 (m)", min_value=1000, max_value=10000, step=500, value=5000)

        if st.button("최적화 실행"):
            with st.spinner("최적화 계산 중..."):
                selected_facility, assignment, not_covered_schools, cumulative_demand = capacitated_MCLP(region_input, coverage_threshold, supply_input)
                st.session_state.optimized = True
                st.session_state.selected_facility = selected_facility
                st.session_state.assignment = assignment
                st.session_state.not_covered_schools = not_covered_schools
                st.session_state.cumulative_demand = cumulative_demand

        if st.session_state.get("optimized", False):
            st.success(f"총 공급된 학생 수: {int(st.session_state.cumulative_demand)}명")
            
            # 표 두 개를 좌우로 배치
            col1_left, col1_right = st.columns([1, 1])

            # 왼쪽: 설치된 시설과 할당 현황
            with col1_left:
                st.markdown("### 📋 설치된 시설과 할당 현황")
                iter_lookup = {
                    (region, fac): iter_num for iter_num, (region, fac) in st.session_state.selected_facility
                }

                rows = []
                for (region, fac), assigned_list in st.session_state.assignment.items():
                    for (school_region, school), amount in assigned_list:
                        rows.append({
                            "설치 Iteration": iter_lookup.get((region, fac), None),
                            "시설명": fac,
                            "할당 학교": school,
                            "할당 인원": int(amount)
                        })

                assign_df = pd.DataFrame(rows).sort_values(["설치 Iteration", "시설명"]).reset_index(drop=True)
                st.dataframe(assign_df, use_container_width=True, hide_index=True)

            # 오른쪽: 충족되지 못한 학교
            with col1_right:
                if st.session_state.not_covered_schools:
                    st.markdown("### ❗ 미충족 학교 현황")
                    not_covered_df = pd.DataFrame(
                        st.session_state.not_covered_schools,
                        columns=["지역", "학교명"]
                    ).reset_index(drop=True)
                    st.dataframe(not_covered_df, use_container_width=True, hide_index=True)
                    st.warning(f"충족되지 못한 학교 수: {len(st.session_state.not_covered_schools)}개")

    with col_mid:
        # 세로 구분선
        st.markdown("<div style='height:1500px; border-left:1px solid lightgray;'></div>", unsafe_allow_html=True)

    with col2:
        if st.session_state.get("optimized", False):
            st.subheader("최적화 결과 지도")
            result_map = map_MCLP(region_input, st.session_state.selected_facility, st.session_state.assignment)
            st_folium(result_map, width=750, height=650)